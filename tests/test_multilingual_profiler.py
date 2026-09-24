"""Unit Tests for Multilingual & Regional Indian Forensic Profiler."""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.detectors.multilingual_profiler import MultilingualProfiler
from tests.test_detectors import generate_natural_voice_mockup


def test_multilingual_profiler_natural_speech():
    profiler = MultilingualProfiler()
    natural_audio = generate_natural_voice_mockup(2.5, 16000)
    result = profiler.analyze(natural_audio, 16000)

    assert "anomaly_score" in result
    assert "metrics" in result
    assert "language_family" in result["metrics"]
    assert "vowel_space_area" in result["metrics"]
    assert "retroflex_dip_ratio" in result["metrics"]
    assert "npvi_rhythm_index" in result["metrics"]
    assert "adaptive_offsets" in result
    assert "pitch_variance_tolerance" in result["adaptive_offsets"]


def test_multilingual_profiler_silence():
    profiler = MultilingualProfiler()
    silent_audio = np.zeros(16000 * 2, dtype=np.float32)
    result = profiler.analyze(silent_audio, 16000)

    assert result["anomaly_score"] == 0.0
    assert result["confidence"] == 0.0
    assert result["metrics"]["language_family"] == "neutral"


def test_multilingual_profiler_vsa_anomaly():
    profiler = MultilingualProfiler()
    # A flat tone has very low formant dispersion and contracted VSA
    t = np.linspace(0, 2.0, 32000, endpoint=False)
    single_tone = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    result = profiler.analyze(single_tone, 16000)

    assert "anomaly_score" in result
    assert result["metrics"]["vowel_space_area"] >= 0.0
