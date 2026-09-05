"""Evaluation and Benchmarking Script for VoxSentinalX Deepfake Models."""
import os
import sys
import argparse
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from typing import Dict, Any

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.lcnn_architecture import LCNNModel
from training.dataset import AudioDeepfakeDataset


def evaluate_model(
    model_path: str = "backend/app/models/pretrained_weights.pt",
    data_dir: str = r"K:\dataSet\archive",
) -> Dict[str, Any]:
    """Runs evaluation benchmark on test data with per-generator breakdown."""
    if not os.path.exists(model_path):
        return {"error": "Model weights file not found."}

    paths = [p.strip() for p in data_dir.split(",") if p.strip()]
    valid_paths = [p for p in paths if os.path.exists(p)]
    if not valid_paths:
        data_dir = "data/synthetic_corpus"
    else:
        data_dir = ",".join(valid_paths)

    dataset = AudioDeepfakeDataset(data_dir=data_dir, fixed_length_sec=2.0, augment=False)
    loader = DataLoader(dataset, batch_size=32, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = LCNNModel(in_channels=1, num_classes=2)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    all_scores = []
    all_labels = []
    all_preds = []
    generator_results: Dict[str, Dict[str, int]] = {}

    # Map sample index to generator
    sample_generators = [s[2] for s in dataset.samples]

    sample_idx = 0
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            logits = model(x)
            probs = F.softmax(logits, dim=1)
            preds = torch.argmax(logits, dim=1)

            scores_np = probs[:, 1].cpu().numpy().tolist()
            labels_np = y.numpy().tolist()
            preds_np = preds.cpu().numpy().tolist()

            all_scores.extend(scores_np)
            all_labels.extend(labels_np)
            all_preds.extend(preds_np)

            for i in range(len(labels_np)):
                gen = sample_generators[sample_idx]
                sample_idx += 1
                if gen not in generator_results:
                    generator_results[gen] = {"total": 0, "correct": 0}
                generator_results[gen]["total"] += 1
                if preds_np[i] == labels_np[i]:
                    generator_results[gen]["correct"] += 1

    y_true = np.array(all_labels)
    y_scores = np.array(all_scores)
    y_pred = np.array(all_preds)

    # Calculate Accuracy, Precision, Recall
    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    tn = np.sum((y_pred == 0) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))

    accuracy = float((tp + tn) / max(len(y_true), 1))
    precision = float(tp / max(tp + fp, 1)) if (tp + fp) > 0 else 0.0
    recall = float(tp / max(tp + fn, 1)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * precision * recall / max(precision + recall, 1e-6))

    # Equal Error Rate (EER)
    thresholds = np.linspace(0.01, 0.99, 100)
    best_diff = float("inf")
    eer = 0.05
    for th in thresholds:
        fpr = np.mean((y_scores >= th) & (y_true == 0))
        fnr = np.mean((y_scores < th) & (y_true == 1))
        diff = abs(fpr - fnr)
        if diff < best_diff:
            best_diff = diff
            eer = (fpr + fnr) / 2.0

    per_generator_metrics = {}
    for gen, res in sorted(generator_results.items()):
        acc = (res["correct"] / max(res["total"], 1)) * 100.0
        per_generator_metrics[gen] = {
            "total_samples": res["total"],
            "correct_predictions": res["correct"],
            "accuracy_percent": round(acc, 2),
        }

    return {
        "samples_evaluated": len(y_true),
        "dataset_path": data_dir,
        "accuracy": round(accuracy * 100.0, 2),
        "precision": round(precision * 100.0, 2),
        "recall": round(recall * 100.0, 2),
        "f1_score": round(f1 * 100.0, 2),
        "equal_error_rate_eer": round(float(eer) * 100.0, 2),
        "confusion_matrix": {
            "true_positives_synthetic": int(tp),
            "false_positives": int(fp),
            "true_negatives_genuine": int(tn),
            "false_negatives": int(fn),
        },
        "per_generator_performance": per_generator_metrics,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate VoxSentinalX Deepfake Model")
    parser.add_argument("--model_path", type=str, default="backend/app/models/pretrained_weights.pt")
    parser.add_argument("--data_dir", type=str, default=r"K:\dataSet\archive")
    args = parser.parse_args()

    metrics = evaluate_model(model_path=args.model_path, data_dir=args.data_dir)
    print("=" * 65)
    print("  VoxSentinalX Model Evaluation Benchmark Results")
    print("=" * 65)
    for k, v in metrics.items():
        if k == "per_generator_performance":
            print("\nPer-Generator Performance:")
            for gen_name, gen_stats in v.items():
                print(f"  [-] {gen_name:20s}: {gen_stats['accuracy_percent']:6.2f}% ({gen_stats['correct_predictions']}/{gen_stats['total_samples']})")
        else:
            print(f"[-] {k}: {v}")
    print("=" * 65)

