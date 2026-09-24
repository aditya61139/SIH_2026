"""Unit Tests for Fusion Scoring Engine and Diagnostic Generation."""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.engine.fusion_scorer import DetectionEngine
from app.engine.diagnostic_generator import DiagnosticGenerator
from tests.test_detectors import generate_natural_voice_mockup, generate_synthetic_clone_mockup


def test_detection_engine_sliding_window():
    engine = DetectionEngine()
    audio = generate_natural_voice_mockup(2.0)

    res = engine.analyze_window(audio, sample_rate=16000, window_index=1, timestamp_sec=1.0)
    assert res["window_index"] == 1
    assert "risk_score" in res
    assert "risk_level" in res
    assert "recommendation" in res
    assert "suggested_actions" in res
    assert "diagnostics" in res
    assert "layer_scores" in res

    # Verify all 10 forensic vectors are present
    expected_vectors = {
        "spectral", "prosody", "breathing", "acoustic_artifacts",
        "lfcc", "glottal", "perturbation", "bispectrum",
        "neural_lcnn", "replay_attack"
    }
    assert set(res["layer_scores"].keys()) == expected_vectors
    assert len(res["layer_scores"]) == 10
    for vec, score in res["layer_scores"].items():
        assert 0.0 <= score <= 1.0, f"Layer score for {vec} out of bounds: {score}"


def test_voice_swap_spike_detection():
    engine = DetectionEngine()
    natural_audio = generate_natural_voice_mockup(2.0)
    synthetic_audio = generate_synthetic_clone_mockup(2.0)

    # Process 3 natural windows
    for i in range(3):
        engine.analyze_window(natural_audio, sample_rate=16000, window_index=i+1, timestamp_sec=float(i))

    # Suddenly switch to synthetic audio
    spike_res = engine.analyze_window(synthetic_audio, sample_rate=16000, window_index=4, timestamp_sec=3.0)
    assert spike_res["risk_score"] > 0.0


def test_diagnostic_generator():
    mock_results = {
        "spectral": {
            "anomaly_score": 0.85,
            "anomalies_detected": [{
                "type": "SPECTRAL_SMOOTHNESS",
                "severity": "HIGH",
                "metric_name": "Spectral Flatness",
                "value": 0.91,
                "threshold": "> 0.70",
                "description": "Unnatural spectral smoothness detected.",
            }]
        }
    }

    report = DiagnosticGenerator.generate_report(risk_score=0.88, detector_results=mock_results, is_spike=True)
    assert report["risk_level"] == "CRITICAL"
    assert len(report["suggested_actions"]) > 0
    assert len(report["anomalies"]) >= 2  # Spike anomaly + spectral anomaly
