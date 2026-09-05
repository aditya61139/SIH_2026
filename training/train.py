"""PyTorch Training Pipeline for VoxSentinalX LCNN Model."""
import os
import sys
import time
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split
from typing import Dict, Any, List

# Ensure UTF-8 stdout if available
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.lcnn_architecture import LCNNModel
from training.dataset import AudioDeepfakeDataset
from training.dataset_generator import generate_training_corpus


class FocalLoss(nn.Module):
    """Focal Loss to combat class imbalance in deepfake detection."""
    def __init__(self, alpha: float = 0.5, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = F.cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * ((1.0 - pt) ** self.gamma) * ce_loss
        return torch.mean(focal_loss)


def compute_eer(scores: np.ndarray, labels: np.ndarray) -> float:
    """Calculates Equal Error Rate (EER)."""
    if len(scores) == 0 or len(np.unique(labels)) < 2:
        return 0.0
    thresholds = np.linspace(0.01, 0.99, 100)
    best_diff = float("inf")
    eer = 0.05
    for th in thresholds:
        fpr = np.mean((scores >= th) & (labels == 0))
        fnr = np.mean((scores < th) & (labels == 1))
        diff = abs(fpr - fnr)
        if diff < best_diff:
            best_diff = diff
            eer = (fpr + fnr) / 2.0
    return float(eer)


def train_model(
    data_dir: str = r"K:\dataSet\archive",
    epochs: int = 10,
    batch_size: int = 32,
    lr: float = 1e-3,
    output_path: str = "backend/app/models/pretrained_weights.pt",
) -> Dict[str, Any]:
    # 1. Check if dataset paths exist
    paths = [p.strip() for p in data_dir.split(",") if p.strip()]
    valid_paths = [p for p in paths if os.path.exists(p)]
    
    if not valid_paths:
        alt_dir = "data/synthetic_corpus"
        print(f"Dataset path(s) {data_dir} not found. Using {alt_dir}...")
        data_dir = alt_dir
        if not os.path.exists(os.path.join(data_dir, "real")) or len(os.listdir(os.path.join(data_dir, "real"))) == 0:
            print(f"Generating synthetic training corpus in {data_dir}...")
            generate_training_corpus(output_dir=data_dir, num_samples_per_class=40)
    else:
        data_dir = ",".join(valid_paths)

    dataset = AudioDeepfakeDataset(data_dir=data_dir, fixed_length_sec=2.0, augment=True)
    if len(dataset) < 4:
        raise ValueError(f"Not enough training samples found in {data_dir}")

    counts = dataset.get_class_counts()
    print("=" * 65)
    print("  VoxSentinalX Deep Neural Training Pipeline (LCNN + BiLSTM)")
    print("=" * 65)
    print(f"Dataset Path: {data_dir}")
    print(f"Total Discovered Audio Samples: {len(dataset)}")
    print("Generator Breakdown:")
    for k, v in counts.items():
        print(f"  [-] {k:20s}: {v:5d} samples")
    print("-" * 65)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(
        dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42),
    )

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=False)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on Device: {device} | Train: {len(train_ds)} | Val: {len(val_ds)} | Batch Size: {batch_size}")
    print("=" * 65)

    model = LCNNModel(in_channels=1, num_classes=2).to(device)
    criterion = FocalLoss(alpha=0.5, gamma=2.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_loss = float("inf")
    best_val_acc = 0.0
    best_eer = 100.0
    history: List[Dict[str, Any]] = []

    total_start_time = time.time()

    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (x, y) in enumerate(train_loader):
            x, y = x.to(device), y.to(device)
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

            batch_size_curr = x.size(0)
            train_loss += loss.item() * batch_size_curr
            preds = torch.argmax(logits, dim=1)
            correct += torch.sum(preds == y).item()
            total += batch_size_curr

            if (batch_idx + 1) % 30 == 0 or (batch_idx + 1) == len(train_loader):
                curr_acc = (correct / total) * 100.0
                curr_loss = train_loss / total
                print(f"  Epoch [{epoch:02d}/{epochs:02d}] Step [{batch_idx+1:03d}/{len(train_loader):03d}] -> Loss: {curr_loss:.4f} | Acc: {curr_acc:.1f}%")

        scheduler.step()
        train_loss /= total
        train_acc = (correct / total) * 100.0

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        val_scores = []
        val_labels = []

        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device)
                logits = model(x)
                loss = criterion(logits, y)
                val_loss += loss.item() * x.size(0)
                preds = torch.argmax(logits, dim=1)
                val_correct += torch.sum(preds == y).item()
                val_total += x.size(0)

                probs = F.softmax(logits, dim=1)
                val_scores.extend(probs[:, 1].cpu().numpy().tolist())
                val_labels.extend(y.cpu().numpy().tolist())

        val_loss = val_loss / max(val_total, 1)
        val_acc = (val_correct / max(val_total, 1)) * 100.0
        val_eer = compute_eer(np.array(val_scores), np.array(val_labels)) * 100.0

        epoch_duration = time.time() - epoch_start
        epoch_stats = {
            "epoch": epoch,
            "train_loss": round(train_loss, 4),
            "train_acc": round(train_acc, 2),
            "val_loss": round(val_loss, 4),
            "val_acc": round(val_acc, 2),
            "val_eer": round(val_eer, 2),
            "duration_sec": round(epoch_duration, 1),
        }
        history.append(epoch_stats)

        print(f"[>] Epoch [{epoch:02d}/{epochs:02d}] Summary ({epoch_duration:.1f}s) | "
              f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.1f}% | "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.1f}%, Val EER: {val_eer:.1f}%")

        # Save Best Model Checkpoint
        if val_loss < best_val_loss or val_acc > best_val_acc:
            if val_loss < best_val_loss:
                best_val_loss = val_loss
            if val_acc > best_val_acc:
                best_val_acc = val_acc
            best_eer = val_eer

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            torch.save(model.state_dict(), output_path)
            # Also save backup in backend models
            archive_backup = os.path.join(os.path.dirname(output_path), "archive_weights.pt")
            torch.save(model.state_dict(), archive_backup)
            print(f"  [SAVED] New best model checkpoint saved to {output_path}")

    total_duration = time.time() - total_start_time
    print("=" * 65)
    print(f"[OK] Training complete in {total_duration:.1f}s! Best Val Acc: {best_val_acc:.2f}%, Best Val EER: {best_eer:.2f}%")
    print("=" * 65)

    return {
        "status": "success",
        "best_val_loss": round(best_val_loss, 4),
        "best_val_acc": round(best_val_acc, 2),
        "best_val_eer": round(best_eer, 2),
        "total_duration_sec": round(total_duration, 1),
        "history": history,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train VoxSentinalX Deep Neural Detector")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--data_dir", type=str, default=r"K:\dataSet\archive")
    parser.add_argument("--output_path", type=str, default="backend/app/models/pretrained_weights.pt")
    args = parser.parse_args()

    train_model(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        output_path=args.output_path,
    )
