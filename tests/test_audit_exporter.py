"""Unit Tests for Cryptographic Forensic Audit Exporter."""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.engine.audit_generator import ForensicAuditGenerator
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_audit_generator_hash_and_signature():
    raw_data = b"Sample simulated voice recording pcm payload"
    sha = ForensicAuditGenerator.compute_sha256(raw_data)
    assert len(sha) == 64

    cert = ForensicAuditGenerator.generate_certificate(
        filename="call_intercept.wav",
        audio_bytes=raw_data,
        duration_sec=4.5,
        overall_verdict="GENUINE_HUMAN",
        risk_level="LOW",
        average_risk_score=0.15,
        peak_risk_score=0.22,
        layer_scores={"spectral": 0.12, "replay_attack": 0.05},
    )

    assert cert["certificate_id"].startswith("VOX-CERT-")
    assert cert["media_metadata"]["sha256_evidence_hash"] == sha
    assert len(cert["media_metadata"]["cryptographic_seal"]) == 64
    assert cert["forensic_verdict"]["overall_verdict"] == "GENUINE_HUMAN"
    assert "ten_layer_vector_scores" in cert
    assert "replay_attack" in cert["ten_layer_vector_scores"]
    assert "legal_compliance" in cert


def test_export_audit_endpoint():
    cert = ForensicAuditGenerator.generate_certificate(
        filename="test.wav",
        duration_sec=3.0,
        overall_verdict="CRITICAL_AI_CLONE",
        risk_level="CRITICAL",
        average_risk_score=0.88,
        peak_risk_score=0.94,
    )

    resp = client.post("/api/export-audit", json={"certificate": cert})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "verified"
    assert data["certificate_id"] == cert["certificate_id"]
    assert "cryptographic_seal" in data
