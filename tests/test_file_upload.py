"""Integration Tests for REST API Endpoints and Audio File Upload."""
import io
import pytest
import soundfile as sf
import numpy as np
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app
from tests.test_detectors import generate_natural_voice_mockup, generate_synthetic_clone_mockup

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["project"] == "VoxSentinalX"


def test_config_endpoint():
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_thresholds" in data
    assert "detector_weights" in data


def test_file_upload_endpoint():
    # Create an in-memory WAV file
    sample_rate = 16000
    audio_data = generate_natural_voice_mockup(3.0, sample_rate)

    wav_io = io.BytesIO()
    sf.write(wav_io, audio_data, sample_rate, format="WAV")
    wav_io.seek(0)

    files = {"file": ("test_voice.wav", wav_io.getvalue(), "audio/wav")}
    resp = client.post("/api/analyze-file", files=files)

    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test_voice.wav"
    assert "overall_verdict" in data
    assert "average_risk_score" in data
    assert "timeline" in data
    assert len(data["timeline"]) >= 1
