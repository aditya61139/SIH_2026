"""Unit Tests for Advanced Forensic Detectors (LFCC, Glottal, Jitter/Shimmer, Bispectrum)."""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.detectors.lfcc_detector import LFCCDetector
from app.detectors.glottal_detector import GlottalFlowDetector
from app.detectors.perturbation_detector import LaryngealPerturbationDetector
from app.detectors.bispectrum_detector import BispectrumPhaseDetector
from tests.test_detectors import generate_natural_voice_mockup, generate_synthetic_clone_mockup


def test_lfcc_detector():
    detector = LFCCDetector()
    natural_audio = generate_natural_voice_mockup(2.0)
    synthetic_audio = generate_synthetic_clone_mockup(2.0)

    res_nat = detector.analyze(natural_audio, 16000)
    res_syn = detector.analyze(synthetic_audio, 16000)

    assert "anomaly_score" in res_nat
    assert "metrics" in res_nat
    assert "hf_lfcc_energy_ratio" in res_nat["metrics"]
    assert res_syn["anomaly_score"] >= 0.0


def test_glottal_detector():
    detector = GlottalFlowDetector()
    natural_audio = generate_natural_voice_mockup(2.0)
    synthetic_audio = generate_synthetic_clone_mockup(2.0)

    res_nat = detector.analyze(natural_audio, 16000)
    res_syn = detector.analyze(synthetic_audio, 16000)

    assert "anomaly_score" in res_nat
    assert "metrics" in res_nat
    assert "naq_mean" in res_nat["metrics"]


def test_perturbation_detector():
    detector = LaryngealPerturbationDetector()
    natural_audio = generate_natural_voice_mockup(2.0)
    synthetic_audio = generate_synthetic_clone_mockup(2.0)

    res_nat = detector.analyze(natural_audio, 16000)
    res_syn = detector.analyze(synthetic_audio, 16000)

    assert "anomaly_score" in res_nat
    assert "metrics" in res_nat
    assert "jitter_local_percent" in res_nat["metrics"]


def test_bispectrum_detector():
    detector = BispectrumPhaseDetector()
    natural_audio = generate_natural_voice_mockup(2.0)
    synthetic_audio = generate_synthetic_clone_mockup(2.0)

    res_nat = detector.analyze(natural_audio, 16000)
    res_syn = detector.analyze(synthetic_audio, 16000)

    assert "anomaly_score" in res_nat
    assert "metrics" in res_nat
    assert "mean_bicoherence" in res_nat["metrics"]
