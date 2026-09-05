"""Unit Tests for Forensic Detectors."""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.detectors.spectral_detector import SpectralDetector
from app.detectors.prosody_detector import ProsodyDetector
from app.detectors.breathing_detector import BreathingDetector
from app.detectors.acoustic_artifacts import AcousticArtifactDetector


def generate_natural_voice_mockup(duration_sec=2.0, sample_rate=16000):
    """Generates synthetic signal simulating natural dynamic pitch and rich harmonics."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Dynamic F0 varying smoothly between 120Hz and 180Hz (sigma ~ 20-30Hz)
    f0 = 150.0 + 35.0 * np.sin(2 * np.pi * 1.5 * t) + 2.0 * np.sin(2 * np.pi * 10.0 * t)  # 10Hz micro-tremor
    phase = 2 * np.pi * np.cumsum(f0) / sample_rate
    # Rich harmonics
    signal = (
        0.5 * np.sin(phase)
        + 0.25 * np.sin(2 * phase)
        + 0.15 * np.sin(3 * phase)
        + 0.08 * np.sin(4 * phase)
    )
    # Add gentle pink/gaussian background noise
    noise = np.random.normal(0, 0.02, len(t))
    return (signal + noise).astype(np.float32)


def generate_synthetic_clone_mockup(duration_sec=2.0, sample_rate=16000):
    """Generates synthetic signal with flat pitch, high spectral flatness, and no tremors."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Perfectly constant F0 = 160.0 Hz (zero variance)
    f0 = 160.0
    phase = 2 * np.pi * f0 * t
    # Flat additive tones with sharp brickwall cutoff
    signal = 0.5 * np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.2 * np.sin(3 * phase)
    # High spectral flatness artifact: add high frequency white noise
    white_noise = np.random.normal(0, 0.15, len(t))
    return (signal + white_noise).astype(np.float32)


def test_spectral_detector():
    detector = SpectralDetector()
    natural_audio = generate_natural_voice_mockup(2.0)
    synthetic_audio = generate_synthetic_clone_mockup(2.0)

    res_nat = detector.analyze(natural_audio, 16000)
    res_syn = detector.analyze(synthetic_audio, 16000)

    assert "anomaly_score" in res_nat
    assert "metrics" in res_nat
    assert res_syn["anomaly_score"] >= res_nat["anomaly_score"]


def test_prosody_detector():
    detector = ProsodyDetector()
    natural_audio = generate_natural_voice_mockup(2.0)
    synthetic_audio = generate_synthetic_clone_mockup(2.0)

    res_nat = detector.analyze(natural_audio, 16000)
    res_syn = detector.analyze(synthetic_audio, 16000)

    assert "anomaly_score" in res_nat
    assert "pitch_std_hz" in res_nat["metrics"]
    # Natural audio has higher pitch std dev than monotone audio
    assert res_nat["metrics"]["pitch_std_hz"] >= res_syn["metrics"].get("pitch_std_hz", 0.0)


def test_breathing_detector():
    detector = BreathingDetector()
    audio = generate_natural_voice_mockup(2.0)

    res = detector.analyze(audio, 16000)
    assert "anomaly_score" in res
    assert "continuous_speech_sec" in res["metrics"]


def test_acoustic_artifact_detector():
    detector = AcousticArtifactDetector()
    audio = generate_synthetic_clone_mockup(2.0)

    res = detector.analyze(audio, 16000)
    assert "anomaly_score" in res
    assert "brickwall_cutoff_detected" in res["metrics"]
