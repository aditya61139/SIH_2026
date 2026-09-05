"""Integration Tests for WebSocket Live Audio Streaming."""
import pytest
import numpy as np
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app
from app.audio.preprocessor import AudioPreprocessor
from tests.test_detectors import generate_natural_voice_mockup


def test_websocket_audio_streaming():
    client = TestClient(app)
    with client.websocket_connect("/ws/analyze") as websocket:
        # Check initial connection payload
        init_data = websocket.receive_json()
        assert init_data["type"] == "CONNECTION_ESTABLISHED"

        # Stream 2.5s of audio in chunks (4096 samples each = 8192 bytes)
        test_audio = generate_natural_voice_mockup(2.5, 16000)
        chunk_size = 4096
        total_chunks = len(test_audio) // chunk_size

        # Send enough chunks to trigger at least 1 window (32000 samples)
        for i in range(8):  # 8 * 4096 = 32768 samples
            chunk = test_audio[i * chunk_size : (i + 1) * chunk_size]
            pcm_bytes = AudioPreprocessor.float32_to_pcm16_bytes(chunk)
            websocket.send_bytes(pcm_bytes)

        # Receive analysis result
        resp = websocket.receive_json()
        assert resp.get("type") == "ANALYSIS_UPDATE"
        assert "risk_score" in resp
        assert "diagnostics" in resp
        assert "layer_scores" in resp
