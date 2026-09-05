"""Laryngeal Micro-Perturbation (Jitter & Shimmer) Forensic Detector."""
import numpy as np
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class LaryngealPerturbationDetector(BaseDetector):
    """
    Measures micro-cycle vocal perturbations:
    1. Jitter (Local, RAP, PPQ5): Fundamental period-to-period variation
    2. Shimmer (Local, APQ3, APQ5): Peak-to-peak amplitude perturbation
    In natural human phonation, neuromuscular tension creates subtle biological micro-instability
    (Jitter: 0.20% - 1.05%, Shimmer: 1.50% - 4.20%).
    Neural TTS synthesizers produce mathematically pure periodicity (Jitter < 0.10%)
    or erratic non-biological phase jitter.
    """

    @property
    def name(self) -> str:
        return "perturbation"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.4 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "jitter_local_percent": 0.0,
                    "shimmer_local_percent": 0.0,
                    "rap_jitter": 0.0,
                    "apq3_shimmer": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. Pitch Period (T0) & Peak Amplitude Extraction via Peak-Picking on Voiced Segments
        periods, amplitudes = self._extract_pitch_cycles(audio, sample_rate)

        if len(periods) < 12:
            return {
                "anomaly_score": 0.1,
                "confidence": 0.4,
                "metrics": {
                    "jitter_local_percent": 0.5,
                    "shimmer_local_percent": 2.5,
                    "rap_jitter": 0.3,
                    "apq3_shimmer": 1.8,
                },
                "anomalies_detected": [],
            }

        # 2. Compute Jitter Metrics
        p = np.array(periods)
        diff_p = np.abs(np.diff(p))
        mean_p = np.mean(p) + 1e-12

        jitter_local = float((np.mean(diff_p) / mean_p) * 100.0)

        # RAP (3-point smoothed)
        rap_diffs = []
        for i in range(1, len(p) - 1):
            smoothed_p = (p[i - 1] + p[i] + p[i + 1]) / 3.0
            rap_diffs.append(abs(p[i] - smoothed_p))
        rap_jitter = float((np.mean(rap_diffs) / mean_p) * 100.0) if rap_diffs else jitter_local

        # 3. Compute Shimmer Metrics
        a = np.array(amplitudes)
        diff_a = np.abs(np.diff(a))
        mean_a = np.mean(a) + 1e-12

        shimmer_local = float((np.mean(diff_a) / mean_a) * 100.0)

        # APQ3 (3-point amplitude perturbation quotient)
        apq3_diffs = []
        for i in range(1, len(a) - 1):
            smoothed_a = (a[i - 1] + a[i] + a[i + 1]) / 3.0
            apq3_diffs.append(abs(a[i] - smoothed_a))
        apq3_shimmer = float((np.mean(apq3_diffs) / mean_a) * 100.0) if apq3_diffs else shimmer_local

        # ── Anomaly Assessment ──
        anomalies = []
        score_components = []

        # Check A: Unnaturally Low Jitter (Machine-perfect periodic synthesis)
        if jitter_local < 0.12:
            score_components.append(0.50)
            anomalies.append({
                "type": "STATIC_LARYNGEAL_JITTER",
                "severity": "HIGH",
                "metric_name": "Laryngeal Cycle-to-Cycle Jitter",
                "value": f"{round(jitter_local, 3)}%",
                "threshold": "< 0.12% (Biological human vocal cords: 0.25% - 1.10%)",
                "description": "Vocal pitch period micro-fluctuation is mathematically static. Lacks natural neuromuscular laryngeal tremor.",
            })
        elif jitter_local > 2.80:
            score_components.append(0.35)
            anomalies.append({
                "type": "ERRATIC_PHASE_JITTER",
                "severity": "MEDIUM",
                "metric_name": "Chaotic Laryngeal Jitter",
                "value": f"{round(jitter_local, 2)}%",
                "threshold": "> 2.80%",
                "description": "Pitch period instability exceeds physiological limits, indicating phase interpolation jitter.",
            })
        else:
            score_components.append(0.0)

        # Check B: Unnaturally Low Shimmer (Sterile amplitude envelope)
        if shimmer_local < 0.90:
            score_components.append(0.40)
            anomalies.append({
                "type": "STERILE_AMPLITUDE_SHIMMER",
                "severity": "MEDIUM",
                "metric_name": "Cycle-to-Cycle Amplitude Shimmer",
                "value": f"{round(shimmer_local, 2)}%",
                "threshold": "< 0.90% (Biological human voice: 1.50% - 4.50%)",
                "description": "Vocal pulse amplitude variation is unnaturally uniform across pitch cycles.",
            })
        else:
            score_components.append(0.0)

        anomaly_score = float(np.clip(np.sum(score_components), 0.0, 1.0))
        confidence = 0.85 if len(periods) >= 30 else 0.60

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "jitter_local_percent": round(jitter_local, 3),
                "shimmer_local_percent": round(shimmer_local, 2),
                "rap_jitter": round(rap_jitter, 3),
                "apq3_shimmer": round(apq3_shimmer, 2),
                "cycles_analyzed": len(periods),
            },
            "anomalies_detected": anomalies,
        }

    def _extract_pitch_cycles(self, audio: np.ndarray, sample_rate: int):
        """Extracts pitch pulse positions and cycle peak amplitudes."""
        # Lowpass filter at 800Hz to emphasize fundamental
        sos = signal.butter(4, 800.0, btype="low", fs=sample_rate, output="sos")
        filtered = signal.sosfilt(sos, audio)

        # Find positive peaks separated by human pitch period limits (70Hz - 400Hz)
        min_distance = int(sample_rate / 400)
        max_distance = int(sample_rate / 70)

        peaks, props = signal.find_peaks(filtered, distance=min_distance, height=0.015)
        if len(peaks) < 3:
            return [], []

        periods = np.diff(peaks)
        # Filter valid pitch periods
        valid_mask = (periods >= min_distance) & (periods <= max_distance)
        if np.sum(valid_mask) < 5:
            return [], []

        valid_periods = periods[valid_mask]
        valid_amplitudes = filtered[peaks[:-1]][valid_mask]

        return valid_periods.tolist(), valid_amplitudes.tolist()
