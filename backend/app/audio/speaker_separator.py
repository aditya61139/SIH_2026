"""Speaker Separation and Voiceprint Calibration Module."""
import numpy as np
from typing import Dict, Any, Optional, Tuple
from app.audio.preprocessor import AudioPreprocessor


class SpeakerSeparator:
    """
    Separates caller voice (from speakerphone) from local user voice.
    Uses calibration acoustic fingerprinting (energy distribution, spectral centroid, rolloff)
    to identify whether speech frames belong to the local user or incoming caller.
    """

    def __init__(self):
        self.is_calibrated: bool = False
        self.user_profile: Dict[str, float] = {
            "mean_energy": 0.0,
            "spectral_centroid": 0.0,
            "spectral_rolloff": 0.0,
        }

    def calibrate(self, user_audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """
        Calibrate user's voiceprint from a short reference phrase.
        Extracts acoustic baseline for local near-field microphone speech.
        """
        if len(user_audio) < sample_rate * 0.5:
            return {"status": "error", "message": "Calibration audio too short (minimum 0.5s required)"}

        # Compute user baseline acoustic metrics
        energy = AudioPreprocessor.compute_rms_energy(user_audio)
        centroid, rolloff = self._compute_spectral_features(user_audio, sample_rate)

        self.user_profile = {
            "mean_energy": float(energy),
            "spectral_centroid": float(centroid),
            "spectral_rolloff": float(rolloff),
        }
        self.is_calibrated = True

        return {
            "status": "success",
            "message": "User voiceprint calibrated successfully",
            "profile": self.user_profile,
        }

    def isolate_caller_audio(self, mixed_audio: np.ndarray, sample_rate: int = 16000) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Extracts caller voice segments from mixed microphone audio.
        If not calibrated, returns full active audio as fallback.
        """
        if len(mixed_audio) == 0:
            return mixed_audio, {"caller_ratio": 0.0, "user_ratio": 0.0}

        if not self.is_calibrated:
            # Fallback: Treat non-silent audio as caller
            return mixed_audio, {"caller_ratio": 1.0, "user_ratio": 0.0, "calibrated": False}

        frame_size = int(0.05 * sample_rate)  # 50ms frames (800 samples)
        if len(mixed_audio) < frame_size:
            return mixed_audio, {"caller_ratio": 1.0, "user_ratio": 0.0}

        num_frames = len(mixed_audio) // frame_size
        frames = [mixed_audio[i * frame_size : (i + 1) * frame_size] for i in range(num_frames)]

        caller_frames = []
        user_frame_count = 0
        caller_frame_count = 0

        for frame in frames:
            if AudioPreprocessor.is_silent(frame, rms_threshold=0.003):
                continue

            frame_energy = AudioPreprocessor.compute_rms_energy(frame)
            frame_centroid, _ = self._compute_spectral_features(frame, sample_rate)

            # Local user speech is characterized by higher near-field energy
            # and closer match to the calibrated centroid
            energy_sim = 1.0 - min(abs(frame_energy - self.user_profile["mean_energy"]) / (self.user_profile["mean_energy"] + 1e-6), 1.0)
            centroid_sim = 1.0 - min(abs(frame_centroid - self.user_profile["spectral_centroid"]) / (self.user_profile["spectral_centroid"] + 1e-6), 1.0)
            user_match_score = 0.5 * energy_sim + 0.5 * centroid_sim

            if user_match_score > 0.70:
                user_frame_count += 1
            else:
                caller_frame_count += 1
                caller_frames.append(frame)

        total_active = user_frame_count + caller_frame_count
        caller_ratio = (caller_frame_count / total_active) if total_active > 0 else 1.0
        user_ratio = (user_frame_count / total_active) if total_active > 0 else 0.0

        if caller_frames:
            isolated_caller = np.concatenate(caller_frames)
            # If separated caller speech is too short for reliable analysis, fall back to mixed audio
            if len(isolated_caller) < int(sample_rate * 0.3):
                isolated_caller = mixed_audio
        else:
            isolated_caller = mixed_audio

        return isolated_caller, {
            "caller_ratio": round(caller_ratio, 2),
            "user_ratio": round(user_ratio, 2),
            "calibrated": True,
        }

    def _compute_spectral_features(self, audio: np.ndarray, sample_rate: int) -> Tuple[float, float]:
        """Computes spectral centroid and spectral rolloff."""
        if len(audio) == 0:
            return 0.0, 0.0

        fft_vals = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)

        sum_fft = np.sum(fft_vals)
        if sum_fft < 1e-6:
            return 0.0, 0.0

        # Spectral Centroid
        centroid = float(np.sum(freqs * fft_vals) / sum_fft)

        # Spectral Rolloff (85% energy point)
        cumsum = np.cumsum(fft_vals)
        rolloff_idx = np.searchsorted(cumsum, 0.85 * sum_fft)
        rolloff = float(freqs[min(rolloff_idx, len(freqs) - 1)])

        return centroid, rolloff
