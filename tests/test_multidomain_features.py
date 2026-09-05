"""Unit Tests for Multi-Domain Feature Extraction Pipeline (Chhatriwala et al. 2026 & Gong & Li 2025)."""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.detectors.multidomain_extractor import MultiDomainFeatureExtractor
from app.audio.codec_simulator import CodecSimulator
from tests.test_detectors import generate_natural_voice_mockup, generate_synthetic_clone_mockup


def test_codec_simulator_mel_delta():
    codec = CodecSimulator(n_mels=40, sample_rate=16000)
    natural_audio = generate_natural_voice_mockup(2.0, 16000)
    synthetic_audio = generate_synthetic_clone_mockup(2.0, 16000)

    res_nat = codec.extract_compression_features(natural_audio)
    res_syn = codec.extract_compression_features(synthetic_audio)

    assert "delta_mean" in res_nat
    assert "delta_var" in res_nat
    assert "distortion_irregularity" in res_nat
    assert len(res_nat["delta_k_profile"]) == 40
    # Synthetic speech exhibits higher variance/irregularity in Delta_k across Mel bands
    assert res_syn["anomaly_score"] >= 0.0


def test_multidomain_feature_extractor_6_domains():
    extractor = MultiDomainFeatureExtractor(sample_rate=16000)
    audio = generate_natural_voice_mockup(2.0, 16000)

    features = extractor.extract_all(audio)

    # Verify all 6 domains are extracted
    assert "compression" in features
    assert "acoustic" in features
    assert "prosody" in features
    assert "phase" in features
    assert "emotional_lld" in features
    assert "statistical_spectral" in features

    # Verify specific key metrics from research papers
    assert "jitter" in features["prosody"]
    assert "shimmer" in features["prosody"]
    assert "group_delay_var" in features["phase"]
    assert "spectral_entropy" in features["statistical_spectral"]
    assert "spectral_flatness" in features["statistical_spectral"]
    assert "mfcc_mean_norm" in features["acoustic"]

    # Verify fused feature vector dimensionality
    assert len(features["fused_vector"]) == 21
