"""Audio Preprocessing and Conversion Utilities."""
import numpy as np
from typing import Tuple


class AudioPreprocessor:
    """Preprocesses raw PCM bytes and converts to standardized 16kHz Float32 format."""

    @staticmethod
    def pcm16_bytes_to_float32(raw_bytes: bytes) -> np.ndarray:
        """Converts raw 16-bit signed integer PCM bytes to normalized float32 array (-1.0 to 1.0)."""
        if not raw_bytes:
            return np.array([], dtype=np.float32)
        int16_samples = np.frombuffer(raw_bytes, dtype=np.int16)
        return int16_samples.astype(np.float32) / 32768.0

    @staticmethod
    def float32_to_pcm16_bytes(audio: np.ndarray) -> bytes:
        """Converts float32 audio array (-1.0 to 1.0) back to 16-bit PCM bytes."""
        clipped = np.clip(audio, -1.0, 1.0)
        int16_samples = (clipped * 32767.0).astype(np.int16)
        return int16_samples.tobytes()

    @staticmethod
    def compute_rms_energy(audio: np.ndarray) -> float:
        """Calculates Root Mean Square (RMS) energy of an audio segment."""
        if len(audio) == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio ** 2)))

    @staticmethod
    def is_silent(audio: np.ndarray, rms_threshold: float = 0.005) -> bool:
        """Determines if the audio segment is silence / background noise."""
        return AudioPreprocessor.compute_rms_energy(audio) < rms_threshold

    @staticmethod
    def normalize_amplitude(audio: np.ndarray, target_peak: float = 0.95) -> np.ndarray:
        """Normalizes audio peak amplitude to prevent clipping and standardize levels."""
        if len(audio) == 0:
            return audio
        max_val = np.max(np.abs(audio))
        if max_val > 1e-6:
            return audio * (target_peak / max_val)
        return audio
