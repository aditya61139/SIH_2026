"""Generate Calibrated Pre-Trained Base Checkpoint for VoxSentinalX LCNN Model."""
import os
import sys
import torch

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.lcnn_architecture import LCNNModel
from training.dataset_generator import generate_training_corpus
from training.train import train_model


def initialize_pretrained_weights():
    weights_path = os.path.abspath(os.path.join(backend_dir, "app", "models", "pretrained_weights.pt"))
    if os.path.exists(weights_path):
        print(f"Pretrained weights already exist at {weights_path}")
        return

    data_dir = os.path.abspath(os.path.join(root_dir, "data", "synthetic_corpus"))
    print("Generating base training corpus...")
    generate_training_corpus(output_dir=data_dir, num_samples_per_class=35)

    print("Training base LCNN-BiLSTM-Attention checkpoint (5 epochs)...")
    train_model(
        data_dir=data_dir,
        epochs=5,
        batch_size=8,
        lr=1e-3,
        output_path=weights_path,
    )


if __name__ == "__main__":
    initialize_pretrained_weights()
