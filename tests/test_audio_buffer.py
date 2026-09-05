"""Unit Tests for Circular Streaming Audio Buffer."""
import pytest
import numpy as np
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.audio.stream_buffer import StreamBuffer
from app.audio.preprocessor import AudioPreprocessor


def test_pcm16_float32_conversion():
    # Generate test float32 samples
    original = np.array([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=np.float32)
    pcm_bytes = AudioPreprocessor.float32_to_pcm16_bytes(original)
    assert len(pcm_bytes) == len(original) * 2

    reconstructed = AudioPreprocessor.pcm16_bytes_to_float32(pcm_bytes)
    assert np.allclose(original, reconstructed, atol=1e-4)


def test_stream_buffer_sliding_window():
    sample_rate = 16000
    window_samples = 32000  # 2.0 seconds
    hop_samples = 16000     # 1.0 second
    capacity_samples = 160000

    buffer = StreamBuffer(
        sample_rate=sample_rate,
        window_samples=window_samples,
        hop_samples=hop_samples,
        capacity_samples=capacity_samples,
    )

    # Ingest 0.5s of audio (8000 samples) -> Should NOT produce a window yet
    chunk_05s = np.zeros(8000, dtype=np.float32)
    win1 = buffer.add_samples(chunk_05s)
    assert win1 is None

    # Ingest another 1.0s (16000 samples, total 24000) -> Still < 32000, no window
    chunk_1s = np.zeros(16000, dtype=np.float32)
    win2 = buffer.add_samples(chunk_1s)
    assert win2 is None

    # Ingest another 0.5s (8000 samples, total 32000) -> Exact window boundary reached!
    chunk_05s_2 = np.ones(8000, dtype=np.float32)
    win3 = buffer.add_samples(chunk_05s_2)
    assert win3 is not None
    assert len(win3) == window_samples
    assert buffer.window_count == 1

    # Ingest another 1.0s (16000 samples = exactly 1 hop) -> Should produce 2nd window
    chunk_1s_2 = np.ones(16000, dtype=np.float32) * 0.5
    win4 = buffer.add_samples(chunk_1s_2)
    assert win4 is not None
    assert len(win4) == window_samples
    assert buffer.window_count == 2


def test_stream_buffer_capacity_eviction():
    sample_rate = 16000
    window_samples = 4000
    hop_samples = 2000
    capacity_samples = 10000  # Cap at 10,000 samples

    buffer = StreamBuffer(
        sample_rate=sample_rate,
        window_samples=window_samples,
        hop_samples=hop_samples,
        capacity_samples=capacity_samples,
    )

    # Ingest 25,000 samples in total
    huge_chunk = np.ones(25000, dtype=np.float32)
    buffer.add_samples(huge_chunk)

    # Internal buffer must not exceed capacity
    assert len(buffer.get_full_buffer()) <= capacity_samples
