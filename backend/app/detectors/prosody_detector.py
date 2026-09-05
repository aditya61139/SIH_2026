"""Prosody, Pitch Variance, and Micro-Tremor Anomaly Detector."""
import numpy as np
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class ProsodyDetector(BaseDetector):
    """
    Analyzes vocal prosody:
    1. Pitch (F0) tracking & inflection variance (sigma)
    2. Involuntary physiological micro-tremors (8-12 Hz jitter)
    3. Syllable duration and cadence uniformity
    """

    @property
    def name(self) -> str:
        return "prosody"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.5 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "pitch_mean_hz": 0.0,
                    "pitch_std_hz": 0.0,
                    "micro_tremor_index": 1.0,
                    "voiced_fraction": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. Pitch (F0) Extraction across 40ms sliding frames
        frame_len = int(0.04 * sample_rate)  # 640 samples (40ms)
        hop_len = int(0.02 * sample_rate)    # 320 samples (20ms)
        
        num_frames = (len(audio) - frame_len) // hop_len
        if num_frames < 5:
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {},
                "anomalies_detected": [],
            }

        f0_track = []
        voiced_count = 0

        for i in range(num_frames):
            frame = audio[i * hop_len : i * hop_len + frame_len]
            if AudioPreprocessor.is_silent(frame, rms_threshold=0.005):
                continue

            # Normalized autocorrelation for F0 estimation
            corr = signal.correlate(frame, frame, mode="full")
            corr = corr[len(corr) // 2 :]
            if corr[0] > 1e-12:
                corr /= corr[0]
                min_lag = int(sample_rate / 450)  # Max 450 Hz
                max_lag = int(sample_rate / 65)   # Min 65 Hz
                
                if len(corr) > max_lag:
                    peak_idx = min_lag + np.argmax(corr[min_lag:max_lag])
                    peak_strength = corr[peak_idx]
                    
                    if peak_strength > 0.40:  # Voiced frame threshold
                        f0 = sample_rate / peak_idx
                        f0_track.append(f0)
                        voiced_count += 1

        voiced_fraction = voiced_count / max(num_frames, 1)

        if len(f0_track) < 8:
            # Insufficient voiced speech
            return {
                "anomaly_score": 0.1,
                "confidence": 0.3,
                "metrics": {
                    "pitch_mean_hz": 0.0,
                    "pitch_std_hz": 0.0,
                    "micro_tremor_index": 0.5,
                    "voiced_fraction": round(voiced_fraction, 2),
                },
                "anomalies_detected": [],
            }

        f0_array = np.array(f0_track)
        pitch_mean = float(np.mean(f0_array))
        pitch_std = float(np.std(f0_array))

        # 2. Micro-Tremor Detection (8-12 Hz frequency fluctuation in F0 contour)
        # In humans, involuntary laryngeal micro-tremors modulate F0 at 8-12 Hz
        f0_detrend = f0_array - np.mean(f0_array)
        if len(f0_detrend) >= 16:
            # Sample rate of F0 contour is 1 / hop_sec = 50 Hz
            f0_fs = 1.0 / (hop_len / sample_rate)  # 50 Hz
            f_tremor, psd_tremor = signal.welch(f0_detrend, fs=f0_fs, nperseg=min(len(f0_detrend), 32))
            tremor_band = (f_tremor >= 8.0) & (f_tremor <= 12.0)
            tremor_power = np.sum(psd_tremor[tremor_band])
            total_f0_power = np.sum(psd_tremor) + 1e-12
            micro_tremor_ratio = float(tremor_power / total_f0_power)
        else:
            micro_tremor_ratio = 0.15

        # ── Anomaly Assessment ──
        anomalies = []
        score_components = []

        # Check A: Abnormally low pitch variance (Monotone robotic cadence or machine-flat pitch)
        if pitch_std < 14.0:
            pitch_score = min((14.0 - pitch_std) / 10.0, 1.0)
            score_components.append(pitch_score * 0.45)
            anomalies.append({
                "type": "MONOTONE_PITCH_ANOMALY",
                "severity": "HIGH" if pitch_std < 8.0 else "MEDIUM",
                "metric_name": "Pitch Variance (σ)",
                "value": f"{round(pitch_std, 1)} Hz",
                "threshold": "< 14.0 Hz (Human normal: 25.0 - 80.0 Hz)",
                "description": "Pitch contour exhibits machine-like uniformity across syllables. Lacks natural emotional inflection.",
            })
        else:
            score_components.append(0.0)

        # Check B: Missing Vocal Micro-Tremors
        if micro_tremor_ratio < 0.04:
            tremor_score = min((0.04 - micro_tremor_ratio) / 0.035, 1.0)
            score_components.append(tremor_score * 0.35)
            anomalies.append({
                "type": "ABSENT_MICRO_TREMOR",
                "severity": "MEDIUM",
                "metric_name": "Vocal Micro-Tremor Index",
                "value": round(micro_tremor_ratio, 4),
                "threshold": "< 0.04 (Human normal: 0.08 - 0.35)",
                "description": "Absence of 8-12 Hz involuntary vocal cord neuromuscular fluctuations.",
            })
        else:
            score_components.append(0.0)

        anomaly_score = float(np.clip(np.sum(score_components), 0.0, 1.0))
        confidence = 0.80 if len(f0_track) >= 20 else 0.55

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "pitch_mean_hz": round(pitch_mean, 1),
                "pitch_std_hz": round(pitch_std, 1),
                "micro_tremor_index": round(micro_tremor_ratio, 4),
                "voiced_fraction": round(voiced_fraction, 2),
            },
            "anomalies_detected": anomalies,
        }
