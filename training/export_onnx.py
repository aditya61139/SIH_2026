"""Export PyTorch Model to ONNX Runtime for Low-Latency Deployment."""
import os
import sys
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.models.lcnn_architecture import LCNNModel


def export_to_onnx(
    weights_path: str = "backend/app/models/pretrained_weights.pt",
    onnx_output_path: str = "backend/app/models/lcnn_deepfake.onnx",
):
    model = LCNNModel(in_channels=1, num_classes=2)
    device = torch.device("cpu")
    if os.path.exists(weights_path):
        model.load_state_dict(torch.load(weights_path, map_location=device))
    model.eval()

    # Dummy input: [Batch=1, Channels=1, Freq=80, Time=200]
    dummy_input = torch.randn(1, 1, 80, 200)

    os.makedirs(os.path.dirname(onnx_output_path), exist_ok=True)
    torch.onnx.export(
        model,
        dummy_input,
        onnx_output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=["melspectrogram_input"],
        output_names=["logits"],
        dynamic_axes={
            "melspectrogram_input": {0: "batch_size", 3: "time_frames"},
            "logits": {0: "batch_size"},
        },
    )
    print(f"[OK] ONNX model successfully exported to {onnx_output_path}")


if __name__ == "__main__":
    export_to_onnx()
