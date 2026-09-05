"""Unit Tests for Multi-Domain Neural Classifier and SHAP Attribution."""
import pytest
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.detectors.neural_classifier import MultiDomainNeuralClassifier
from app.detectors.multidomain_extractor import MultiDomainFeatureExtractor
from tests.test_detectors import (
    generate_natural_voice_mockup,
    generate_synthetic_clone_mockup,
    generate_indian_dialect_voice_mockup,
)


def test_neural_classifier_forward_pass():
    classifier = MultiDomainNeuralClassifier(input_dim=21, hidden_dim=128)
    dummy_features = np.zeros(21, dtype=np.float32)

    p_gen, p_syn, shap = classifier.predict_proba(dummy_features)

    assert 0.0 <= p_gen <= 1.0
    assert 0.0 <= p_syn <= 1.0
    assert np.isclose(p_gen + p_syn, 1.0, atol=1e-4)

    # Check that SHAP covers all 6 domains
    assert "compression" in shap
    assert "acoustic" in shap
    assert "prosody" in shap
    assert "phase" in shap
    assert "emotional" in shap
    assert "statistical_spectral" in shap


def test_neural_classifier_synthetic_vs_genuine():
    extractor = MultiDomainFeatureExtractor(sample_rate=16000)
    classifier = MultiDomainNeuralClassifier(input_dim=21, hidden_dim=128)

    natural_audio = generate_natural_voice_mockup(2.5, 16000)
    synthetic_audio = generate_synthetic_clone_mockup(2.5, 16000)

    feat_nat = extractor.extract_all(natural_audio)
    feat_syn = extractor.extract_all(synthetic_audio)

    _, p_syn_nat, shap_nat = classifier.predict_proba(feat_nat["fused_vector"])
    _, p_syn_syn, shap_syn = classifier.predict_proba(feat_syn["fused_vector"])

    assert p_syn_syn >= p_syn_nat
    assert shap_syn["compression"] >= 0.0


def test_indian_dialect_phonetic_calibration():
    extractor = MultiDomainFeatureExtractor(sample_rate=16000)
    classifier = MultiDomainNeuralClassifier(input_dim=21, hidden_dim=128)

    indian_voice = generate_indian_dialect_voice_mockup(2.5, 16000)
    features = extractor.extract_all(indian_voice)

    # Verify D1 compression anomaly score is calibrated (low on genuine Indian speech)
    assert features["compression"]["anomaly_score"] <= 0.20

    p_gen, p_syn, shap = classifier.predict_proba(features["fused_vector"])
    
    # Authentic Indian speech must be classified as genuine (low synthetic probability)
    assert p_syn <= 0.25
    assert p_gen >= 0.75
    # SHAP distribution must be balanced across domains rather than 100% on compression
    assert shap["compression"] < 0.60
