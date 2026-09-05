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


def _create_mock_mp4_audio(audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Helper to encode raw PCM into an AAC/MP4 container using bundled FFmpeg."""
    import imageio_ffmpeg
    import subprocess
    import tempfile
    
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    int16_samples = (audio_data * 32767).astype(np.int16)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        cmd = [
            ffmpeg_exe, "-y",
            "-f", "s16le", "-ar", str(sample_rate), "-ac", "1",
            "-i", "-",
            "-c:a", "aac", "-b:a", "128k",
            tmp_path
        ]
        subprocess.run(
            cmd,
            input=int16_samples.tobytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_mp4_video_container_upload():
    """Test demuxing and analyzing audio from an uploaded MP4 container."""
    sample_rate = 16000
    audio_data = generate_synthetic_clone_mockup(3.0, sample_rate)
    mp4_bytes = _create_mock_mp4_audio(audio_data, sample_rate)
    assert len(mp4_bytes) > 0

    files = {"file": ("deepfake_speech.mp4", mp4_bytes, "video/mp4")}
    resp = client.post("/api/analyze-file", files=files)

    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "deepfake_speech.mp4"
    assert data["duration_seconds"] > 2.5
    assert data["overall_verdict"] in [
        "GENUINE_HUMAN",
        "INCONCLUSIVE_SUSPICIOUS",
        "PROBABLE_SYNTHETIC",
        "CRITICAL_AI_CLONE",
        "AUTHENTIC",
        "HIGH_RISK_CLONE",
    ]
    assert "domain_shap_contributions" in data
    assert "compression" in data["domain_shap_contributions"]
    assert len(data["timeline"]) >= 1


def test_audio_decoder_direct():
    """Unit test AudioDecoder against WAV and MP4 inputs."""
    from app.audio.decoder import AudioDecoder
    sample_rate = 16000
    original_audio = generate_natural_voice_mockup(2.0, sample_rate)

    # Test WAV decoding
    wav_io = io.BytesIO()
    sf.write(wav_io, original_audio, sample_rate, format="WAV")
    decoded_wav, duration_wav = AudioDecoder.decode_to_16k_mono(wav_io.getvalue(), "voice.wav")
    assert isinstance(decoded_wav, np.ndarray)
    assert decoded_wav.dtype == np.float32
    assert abs(duration_wav - 2.0) < 0.1

    # Test MP4 decoding
    mp4_bytes = _create_mock_mp4_audio(original_audio, sample_rate)
    decoded_mp4, duration_mp4 = AudioDecoder.decode_to_16k_mono(mp4_bytes, "video.mp4")
    assert isinstance(decoded_mp4, np.ndarray)
    assert decoded_mp4.dtype == np.float32
    assert abs(duration_mp4 - 2.0) < 0.2

