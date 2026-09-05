"""Circular Streaming Audio Buffer with Sliding Window Management."""
import numpy as np
from typing import Optional, Tuple
from app.core.config import settings
from app.audio.preprocessor import AudioPreprocessor


class StreamBuffer:
    """
    Circular sliding-window buffer for continuous real-time audio streams.
    Manages incoming PCM chunks and produces overlapping analysis windows.
    """

    def __init__(
        self,
        sample_rate: int = settings.SAMPLE_RATE,
        window_samples: int = settings.WINDOW_SAMPLES,
        hop_samples: int = settings.HOP_SAMPLES,
        capacity_samples: int = settings.BUFFER_CAPACITY_SAMPLES,
    ):
        self.sample_rate = sample_rate
        self.window_samples = window_samples
        self.hop_samples = hop_samples
        self.capacity_samples = capacity_samples

        self._buffer = np.array([], dtype=np.float32)
        self._samples_since_hop = 0
        self._total_ingested_samples = 0
        self._window_count = 0

    def add_pcm16_bytes(self, raw_bytes: bytes) -> Optional[np.ndarray]:
        """
        Ingests raw Int16 PCM bytes from WebSocket.
        Returns a new analysis window (Float32 array of length WINDOW_SAMPLES)
        if enough new samples have accumulated, otherwise returns None.
        """
        float32_chunk = AudioPreprocessor.pcm16_bytes_to_float32(raw_bytes)
        return self.add_samples(float32_chunk)

    def add_samples(self, float32_samples: np.ndarray) -> Optional[np.ndarray]:
        """
        Ingests Float32 audio samples.
        Returns ready 2.0s window if a hop boundary has been reached.
        """
        if len(float32_samples) == 0:
            return None

        self._buffer = np.concatenate([self._buffer, float32_samples])
        self._samples_since_hop += len(float32_samples)
        self._total_ingested_samples += len(float32_samples)

        # Evict oldest samples if buffer exceeds circular capacity
        if len(self._buffer) > self.capacity_samples:
            self._buffer = self._buffer[-self.capacity_samples:]

        # Check if we have accumulated enough data for a new hop & full window
        if self._samples_since_hop >= self.hop_samples and len(self._buffer) >= self.window_samples:
            self._samples_since_hop = 0
            self._window_count += 1
            # Return the latest window of exact length window_samples
            return self._buffer[-self.window_samples:].copy()

        return None

    @property
    def window_count(self) -> int:
        return self._window_count

    @property
    def total_duration_seconds(self) -> float:
        return self._total_ingested_samples / self.sample_rate

    def get_full_buffer(self) -> np.ndarray:
        """Returns the entire current active buffer."""
        return self._buffer.copy()

    def reset(self) -> None:
        """Clears buffer and state."""
        self._buffer = np.array([], dtype=np.float32)
        self._samples_since_hop = 0
        self._total_ingested_samples = 0
        self._window_count = 0
