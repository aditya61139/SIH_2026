"""Respiration and Breathing Pattern Anomaly Detector."""
import numpy as np
from typing import Dict, Any, List, Optional
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class BreathingDetector(BaseDetector):
    """
    Monitors speech respiration dynamics:
    1. Inhalation pause frequency
    2. Continuous speech duration without respiration events
    3. Low-amplitude unvoiced breath sound spectral signature
    """

    def __init__(self):
        self._continuous_speech_seconds = 0.0
        self._breath_event_count = 0

    @property
    def name(self) -> str:
        return "breathing"

    def analyze(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
        hop_duration_sec: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        if len(audio) == 0:
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "breath_events_detected": 0,
                    "continuous_speech_sec": 0.0,
                    "pause_fraction": 0.0,
                },
                "anomalies_detected": [],
            }

        duration_sec = len(audio) / sample_rate
        # For sliding windows (e.g. 2.0s window with 1.0s hop), advance the accumulator
        # by the actual hop step rather than the full window length to avoid time dilation.
        time_step_sec = hop_duration_sec if hop_duration_sec is not None else (1.0 if duration_sec >= 2.0 else duration_sec)

        frame_len = int(0.05 * sample_rate)  # 50ms analysis frames
        num_frames = len(audio) // frame_len

        # Extract frame energies and zero-crossing rates
        energies = []
        zero_crossings = []
        for i in range(num_frames):
            frame = audio[i * frame_len : (i + 1) * frame_len]
            energies.append(AudioPreprocessor.compute_rms_energy(frame))
            zc = np.sum(np.abs(np.diff(np.signbit(frame)))) / (2.0 * len(frame))
            zero_crossings.append(zc)

        energies = np.array(energies)
        zero_crossings = np.array(zero_crossings)

        speech_frames = energies > 0.01
        pause_frames = ~speech_frames
        pause_fraction = float(np.mean(pause_frames))

        # Potential inhalation cues: quiet unvoiced aspiration (low energy, higher zero-crossing rate)
        breath_candidates = (energies >= 0.003) & (energies <= 0.02) & (zero_crossings > 0.15)
        num_breath_events = int(np.sum(breath_candidates))

        if np.mean(speech_frames) > 0.85:
            self._continuous_speech_seconds += time_step_sec
        else:
            self._continuous_speech_seconds = max(0.0, self._continuous_speech_seconds - time_step_sec * 0.5)

        if num_breath_events > 0:
            self._breath_event_count += num_breath_events
            # Detected pause/breath relaxes continuous speech accumulator
            self._continuous_speech_seconds = max(0.0, self._continuous_speech_seconds - 3.0)

        anomalies = []
        anomaly_score = 0.0

        # Most speakers take an inhalation pause within 6-8 seconds of continuous phonation
        if self._continuous_speech_seconds >= 6.0 and self._breath_event_count == 0:
            severity = "CRITICAL" if self._continuous_speech_seconds >= 10.0 else "HIGH"
            anomaly_score = min((self._continuous_speech_seconds - 5.0) / 7.0, 1.0)
            anomalies.append({
                "type": "ABSENT_BREATHING_PATTERN",
                "severity": severity,
                "metric_name": "Continuous Speech Without Respiration",
                "value": f"{round(self._continuous_speech_seconds, 1)}s",
                "threshold": "> 6.0s (Natural human pause limit: ~4.0 - 8.0s)",
                "description": "Continuous speech detected without expected inhalation pauses, typical of uninterrupted synthetic audio generation.",
            })

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": 0.80 if duration_sec >= 2.0 else 0.50,
            "metrics": {
                "breath_events_detected": num_breath_events,
                "continuous_speech_sec": round(self._continuous_speech_seconds, 1),
                "pause_fraction": round(pause_fraction, 3),
            },
            "anomalies_detected": anomalies,
        }

    def reset(self) -> None:
        """Reset state."""
        self._continuous_speech_seconds = 0.0
        self._breath_event_count = 0
