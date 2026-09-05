"""Unit Tests for Deep Neural LCNN Model and Training Inference."""
import pytest
import os
import sys
import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.lcnn_architecture import LCNNModel
from app.detectors.neural_lcnn_detector import NeuralLCNNDetector
from tests.test_detectors import generate_natural_voice_mockup


def test_lcnn_forward_pass():
    model = LCNNModel(in_channels=1, num_classes=2)
    model.eval()

    # Input: [Batch=2, Channels=1, Freq=80, Time=128]
    x = torch.randn(2, 1, 80, 128)
    with torch.no_grad():
        out = model(x)

    assert out.shape == (2, 2)


def test_neural_detector_inference():
    detector = NeuralLCNNDetector()
    audio = generate_natural_voice_mockup(2.0, 16000)

    res = detector.analyze(audio, 16000)
    assert "anomaly_score" in res
    assert "metrics" in res
    assert "neural_spoof_prob" in res["metrics"]
