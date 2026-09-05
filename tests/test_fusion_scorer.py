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


def test_genuine_voice_low_risk_score():
    """Verify that natural human speech yields a low risk score (< 0.35)."""
    engine = DetectionEngine()
    natural_audio = generate_natural_voice_mockup(2.0, 16000)

    res = engine.analyze_window(natural_audio, sample_rate=16000, window_index=1, timestamp_sec=0.0)
    assert res["risk_score"] < 0.35
    assert res["risk_level"] in ["LOW", "MODERATE"]
    assert res["neural_synthetic_probability"] < 0.35


def test_silence_rapid_risk_decay():
    """Verify that when speech stops and silence occurs, the risk score drops rapidly."""
    engine = DetectionEngine()
    synthetic_audio = generate_synthetic_clone_mockup(2.0, 16000)
    silent_audio = np.zeros(32000, dtype=np.float32)

    # 1. Trigger synthetic detection
    res_synth = engine.analyze_window(synthetic_audio, sample_rate=16000, window_index=1, timestamp_sec=0.0)
    initial_score = res_synth["risk_score"]
    assert initial_score > 0.35

    # 2. Feed silence windows
    res_silence1 = engine.analyze_window(silent_audio, sample_rate=16000, window_index=2, timestamp_sec=2.0)
    assert res_silence1["risk_score"] < initial_score
    assert "Ambient Room / Silence" in res_silence1["status_text"]

    res_silence2 = engine.analyze_window(silent_audio, sample_rate=16000, window_index=3, timestamp_sec=4.0)
    res_silence3 = engine.analyze_window(silent_audio, sample_rate=16000, window_index=4, timestamp_sec=6.0)
    assert res_silence3["risk_score"] <= 0.05
    assert res_silence3["risk_level"] == "LOW"


def test_engine_reset():
    """Verify that engine reset clears history and EMA score."""
    engine = DetectionEngine()
    synthetic_audio = generate_synthetic_clone_mockup(2.0, 16000)
    engine.analyze_window(synthetic_audio, sample_rate=16000, window_index=1, timestamp_sec=0.0)
    assert engine.current_ema_score > 0.0

    engine.reset()
    assert engine.current_ema_score == 0.0
    assert len(engine.history_scores) == 0
    assert engine.total_windows_processed == 0

