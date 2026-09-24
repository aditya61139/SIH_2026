"""Unit Tests for Physical Replay Attack Detector (Robust & Calibrated for Loud Voices)."""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.detectors.replay_detector import ReplayDetector
from tests.test_detectors import generate_natural_voice_mockup
from training.dataset_generator import (
    generate_loud_genuine_speech_sample,
    generate_loudspeaker_replayed_sample,
)


def test_replay_detector_clean_voice():
    detector = ReplayDetector()
    clean_audio = generate_natural_voice_mockup(2.0, 16000)
    result = detector.analyze(clean_audio, 16000)

    assert "anomaly_score" in result
    assert "metrics" in result
    assert "thd_score" in result["metrics"]
    assert "rt60_ratio" in result["metrics"]
    assert "replay_probability" in result["metrics"]
    # Clean natural voice should have low replay probability
    assert result["metrics"]["replay_probability"] < 0.30
    assert len(result["anomalies_detected"]) == 0


def test_loud_genuine_voice_does_not_trigger_replay():
    """
    CRITICAL REGRESSION TEST FOR LOUD SPEECH:
    Speaking loudly (high amplitude, strong formants, elevated pitch)
    must NOT be falsely flagged as a loudspeaker replay attack.
    """
    detector = ReplayDetector()

    # Test multiple durations and loud speech generations
    for dur in [2.0, 3.0]:
        loud_audio = generate_loud_genuine_speech_sample(dur, 16000)
        # Ensure high volume / amplitude
        loud_audio = loud_audio * 1.5
        loud_audio = np.clip(loud_audio, -1.0, 1.0)

        result = detector.analyze(loud_audio, 16000)

        # Verify replay probability is strictly suppressed for loud authentic voice
        assert result["metrics"]["replay_probability"] < 0.30, (
            f"Loud speech triggered high replay prob: {result['metrics']['replay_probability']}"
        )
        assert result["anomaly_score"] < 0.30
        assert len(result["anomalies_detected"]) == 0, (
            f"Loud speech triggered false anomalies: {result['anomalies_detected']}"
        )
        # HNR should be high for genuine loud voice
        assert result["metrics"]["hnr_db"] >= 15.0


def test_female_elevated_pitch_does_not_trigger_coloration():
    """
    Elevated pitch (>160 Hz) naturally lacks energy below 150 Hz.
    The detector must condition sub-bass checks on pitch to prevent false coloration penalties.
    """
    detector = ReplayDetector()
    t = np.linspace(0, 2.0, 32000, endpoint=False)
    # Pitch fundamental at 230 Hz with formants
    f0 = 230.0
    phase = 2 * np.pi * f0 * t
    voice = 0.6 * np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.15 * np.sin(3 * phase)
    voice = voice.astype(np.float32)

    result = detector.analyze(voice, 16000)
    assert result["metrics"]["coloration_score"] < 0.40
    assert result["metrics"]["replay_probability"] < 0.30


def test_replay_detector_replayed_audio():
    detector = ReplayDetector()
    replayed_audio = generate_loudspeaker_replayed_sample(2.5, 16000)
    result = detector.analyze(replayed_audio, 16000)

    assert "anomaly_score" in result
    assert result["confidence"] > 0.60
    assert result["metrics"]["replay_probability"] >= 0.0


def test_replay_detector_silence():
    detector = ReplayDetector()
    silent_audio = np.zeros(16000 * 2, dtype=np.float32)
    result = detector.analyze(silent_audio, 16000)
    assert result["anomaly_score"] == 0.0
    assert result["confidence"] == 0.0
