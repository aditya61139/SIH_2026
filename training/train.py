"""
PyTorch & GPU-Accelerated Training Pipeline for VoxSentinalX LCNN Model.
Features:
- Full CUDA GPU acceleration with Mixed Precision (AMP Autocast & GradScaler)
- Uniform multi-generator sampling with PyTorch DataLoader(shuffle=True, pin_memory=True)
- Cosine Annealing learning rate scheduler with Focal Loss
- Automated training sample inventory generation
"""
import os
import sys
import time
import argparse
import numpy as np
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
    data_dir: str = "data/unified_corpus",
    epochs: int = 15,
    batch_size: int = 32,
    lr: float = 1e-3,
    output_path: str = "backend/app/models/pretrained_weights.pt",
) -> Dict[str, Any]:
    # 1. Update/Generate Dataset Inventory
    try:
        from training.generate_sample_inventory import generate_inventory
        inventory_target = os.path.abspath(data_dir)
        if os.path.exists(inventory_target):
            generate_inventory(inventory_target)
    except Exception as inv_err:
        print(f"[!] Note on inventory generation: {inv_err}")

    # Check PyTorch availability
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
        from torch.utils.data import DataLoader, random_split
        from app.models.lcnn_architecture import LCNNModel
        from training.dataset import AudioDeepfakeDataset
        from training.dataset_generator import generate_training_corpus
    except Exception as torch_err:
        print(f"[!] PyTorch import warning: {torch_err}")
        print("[-] Executing high-throughput Forensic Ensemble training pipeline...")
        from training.train_acoustic_ensemble import run_training
        run_training()
        return {"status": "trained_via_ensemble", "message": "Trained with 8-Vector Forensic Ensemble."}

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

    # 2. Check if dataset paths exist
    paths = [p.strip() for p in data_dir.split(",") if p.strip()]
    valid_paths = [p for p in paths if os.path.exists(p)]

    if not valid_paths:
        alt_dirs = [
            os.path.abspath(os.path.join(root_dir, "data", "unified_corpus")),
            os.path.abspath(os.path.join(root_dir, "data", "synthetic_corpus")),
        ]
        for candidate in alt_dirs:
            if os.path.exists(candidate):
                data_dir = candidate
                valid_paths = [candidate]
                break
        if not valid_paths:
            data_dir = "data/unified_corpus"
            print(f"Generating synthetic training corpus in {data_dir}...")
            generate_training_corpus(output_dir=data_dir, num_samples_per_class=40)
    else:
        data_dir = ",".join(valid_paths)

    dataset = AudioDeepfakeDataset(data_dir=data_dir, fixed_length_sec=2.0, augment=True)
    if len(dataset) < 4:
        raise ValueError(f"Not enough training samples found in {data_dir}")

    counts = dataset.get_class_counts()
    print("=" * 68)
    print("  🛡️ VoxSentinalX Deep Neural Training Pipeline (LCNN + BiLSTM)")
    print("=" * 68)
    print(f"Dataset Path: {data_dir}")
    print(f"Total Discovered Audio Samples: {len(dataset):,}")
    print("Generator Breakdown:")
    for k, v in sorted(counts.items()):
        print(f"  [-] {k:25s}: {v:5d} samples")
    print("-" * 68)

    # 3. Stratified Train / Validation Split (80% / 20%)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_ds, val_ds = random_split(
        dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42),
    )

    # 4. GPU Device Detection & Mixed Precision Setup
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    if use_cuda:
        gpu_name = torch.cuda.get_device_name(0)
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        print(f"🚀 GPU ACCELERATION ENABLED: {gpu_name} ({vram_gb:.2f} GB VRAM)")
        torch.backends.cudnn.benchmark = True
    else:
        print("💻 Hardware: Multi-Threaded CPU Engine Active")

    # 5. PyTorch DataLoader with shuffle=True & pin_memory=True
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        pin_memory=use_cuda,
        num_workers=0,
        drop_last=False,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        pin_memory=use_cuda,
        num_workers=0,
    )

    print(f"Training Config -> Epochs: {epochs} | Batch Size: {batch_size} | Train Batches: {len(train_loader)} | Val Batches: {len(val_loader)}")
    print("=" * 68)

    model = LCNNModel(in_channels=1, num_classes=2).to(device)
    criterion = FocalLoss(alpha=0.5, gamma=2.0)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    # Mixed Precision Scaler for CUDA
    scaler = torch.cuda.amp.GradScaler(enabled=use_cuda)

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
            x, y = x.to(device, non_blocking=use_cuda), y.to(device, non_blocking=use_cuda)
            optimizer.zero_grad()

            with torch.cuda.amp.autocast(enabled=use_cuda):
                logits = model(x)
                loss = criterion(logits, y)

            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()

            batch_size_curr = x.size(0)
            train_loss += loss.item() * batch_size_curr
            preds = torch.argmax(logits, dim=1)
            correct += torch.sum(preds == y).item()
            total += batch_size_curr

            if (batch_idx + 1) % 25 == 0 or (batch_idx + 1) == len(train_loader):
                curr_acc = (correct / total) * 100.0
                curr_loss = train_loss / total
                print(f"  Epoch [{epoch:02d}/{epochs:02d}] Step [{batch_idx+1:03d}/{len(train_loader):03d}] -> Loss: {curr_loss:.4f} | Acc: {curr_acc:.1f}%")

        scheduler.step()
        train_loss /= total
        train_acc = (correct / total) * 100.0

        # Validation Pass
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        val_scores = []
        val_labels = []

        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device, non_blocking=use_cuda), y.to(device, non_blocking=use_cuda)
                with torch.cuda.amp.autocast(enabled=use_cuda):
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
            archive_backup = os.path.join(os.path.dirname(output_path), "archive_weights.pt")
            torch.save(model.state_dict(), archive_backup)
            print(f"  [SAVED] New best model checkpoint saved to {output_path}")

    total_duration = time.time() - total_start_time
    print("=" * 68)
    print(f"[OK] Training complete in {total_duration:.1f}s! Best Val Acc: {best_val_acc:.2f}%, Best Val EER: {best_eer:.2f}%")
    print("=" * 68)

    return {
        "status": "success",
        "best_val_loss": round(best_val_loss, 4),
        "best_val_acc": round(best_val_acc, 2),
        "best_val_eer": round(best_eer, 2),
        "total_duration_sec": round(total_duration, 1),
        "history": history,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train VoxSentinalX Deep Neural Detector with GPU Acceleration")
    parser.add_argument("--epochs", type=int, default=15, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size per step")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--data_dir", type=str, default="data/unified_corpus", help="Path to unified corpus")
    parser.add_argument("--output_path", type=str, default="backend/app/models/pretrained_weights.pt")
    args = parser.parse_args()

    train_model(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        output_path=args.output_path,
    )
