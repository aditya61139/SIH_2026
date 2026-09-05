"""Prosody, Pitch Variance, Jitter, Shimmer, and Micro-Tremor Anomaly Detector (Domain 3).
Based on:
- Chhatriwala et al. (ITEGAM-JETIA 2026), Equations 4 & 5.
- Gong & Li (MDPI Electronics 2025), F0 Linear Interpolation across silence.
"""
import numpy as np
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class ProsodyDetector(BaseDetector):
    """
    Analyzes vocal prosody:
    1. Pitch (F0) tracking & dynamic variance (sigma) with linear silence interpolation
    2. Jitter (relative period perturbation between consecutive cycles)
    3. Shimmer (relative amplitude perturbation between consecutive cycles)
    4. Involuntary physiological micro-tremors (8-12 Hz jitter)
    """

    @property
    def name(self) -> str:
        return "prosody"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.2 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "pitch_mean_hz": 0.0,
                    "pitch_std_hz": 0.0,
                    "jitter": 0.0,
                    "shimmer": 0.0,
                    "micro_tremor_index": 1.0,
                    "voiced_fraction": 0.0,
                },
                "anomalies_detected": [],
            }

        frame_len = int(0.030 * sample_rate)  # 30ms frames
        hop_len = int(0.010 * sample_rate)    # 10ms hop
        num_frames = max(1, (len(audio) - frame_len) // hop_len)

        f0_raw = []
        peak_amps = []
        periods = []

        for i in range(num_frames):
            frame = audio[i * hop_len : i * hop_len + frame_len]
            if AudioPreprocessor.is_silent(frame, rms_threshold=0.004):
                f0_raw.append(np.nan)
                continue

            corr = signal.correlate(frame, frame, mode="full")
            corr = corr[len(corr) // 2 :]
            if corr[0] > 1e-10:
                corr /= corr[0]
                min_lag = int(sample_rate / 450)
                max_lag = int(sample_rate / 65)
                if len(corr) > max_lag:
                    peak_idx = min_lag + np.argmax(corr[min_lag:max_lag])
                    if corr[peak_idx] > 0.35:
                        f0_val = sample_rate / peak_idx
                        f0_raw.append(f0_val)
                        periods.append(1.0 / f0_val)
                        peak_amps.append(np.max(np.abs(frame)))
                    else:
                        f0_raw.append(np.nan)
                else:
                    f0_raw.append(np.nan)
            else:
                f0_raw.append(np.nan)

        f0_array = np.array(f0_raw)
        voiced_count = np.sum(~np.isnan(f0_array))
        voiced_fraction = float(voiced_count / max(num_frames, 1))

        # If window contains insufficient voiced speech (< 5 frames), treat as neutral/unvoiced
        valid_idx = np.where(~np.isnan(f0_array))[0]
        if len(valid_idx) < 5 or voiced_fraction < 0.15:
            return {
                "anomaly_score": 0.0,
                "confidence": 0.20,
                "metrics": {
                    "pitch_mean_hz": 150.0,
                    "pitch_std_hz": 25.0,
                    "jitter": 0.025,
                    "shimmer": 0.065,
                    "micro_tremor_index": 0.15,
                    "voiced_fraction": round(voiced_fraction, 2),
                },
                "anomalies_detected": [],
            }

        # Linear Interpolation across unvoiced/silent periods (Gong & Li 2025)
        interp_f0 = np.interp(np.arange(len(f0_array)), valid_idx, f0_array[valid_idx])
        pitch_mean = float(np.mean(interp_f0))
        pitch_std = float(np.std(interp_f0))

        # ── Jitter Calculation (Equation 4): Period Perturbation ──
        if len(periods) >= 5:
            p_arr = np.array(periods)
            mean_p = np.mean(p_arr)
            jitter = float(np.mean(np.abs(np.diff(p_arr))) / (mean_p + 1e-8))
        else:
            jitter = 0.025

        # ── Shimmer Calculation (Equation 5): Amplitude Perturbation ──
        if len(peak_amps) >= 5:
            a_arr = np.array(peak_amps)
            mean_a = np.mean(a_arr)
            shimmer = float(np.mean(np.abs(np.diff(a_arr))) / (mean_a + 1e-8))
        else:
            shimmer = 0.065

        # ── Micro-Tremor Detection (8-12 Hz F0 fluctuations) ──
        if len(valid_idx) >= 16:
            f0_detrend = interp_f0 - np.mean(interp_f0)
            f0_fs = 1.0 / (hop_len / sample_rate)  # 100 Hz
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

        # Check A: Low Jitter (Machine-quantized periodicity in voiced frames)
        if jitter < 0.005 and voiced_fraction >= 0.35:
            j_score = min((0.005 - jitter) / 0.004, 1.0)
            score_components.append(j_score * 0.40)
            anomalies.append({
                "type": "LOW_JITTER_ANOMALY",
                "severity": "HIGH" if jitter < 0.002 else "MEDIUM",
                "metric_name": "Pitch Jitter Perturbation",
                "value": f"{round(jitter * 100, 2)}%",
                "threshold": "< 0.50% (Human normal: 0.8% - 6.5%)",
                "description": "Vocal period lacks natural human glottal cycle perturbations. Machine-quantized periodicity.",
            })
        else:
            score_components.append(0.0)

        # Check B: Low Shimmer (Machine amplitude sterility in voiced frames)
        if shimmer < 0.016 and voiced_fraction >= 0.35:
            s_score = min((0.016 - shimmer) / 0.012, 1.0)
            score_components.append(s_score * 0.35)
            anomalies.append({
                "type": "LOW_SHIMMER_ANOMALY",
                "severity": "HIGH" if shimmer < 0.008 else "MEDIUM",
                "metric_name": "Vocal Shimmer Perturbation",
                "value": f"{round(shimmer * 100, 2)}%",
                "threshold": "< 1.6% (Human normal: 2.5% - 16.0%)",
                "description": "Vocal cycle amplitude is unnaturally sterile, lacking biological subglottal pressure micro-variations.",
            })
        else:
            score_components.append(0.0)

        # Check C: Low Pitch Variance (Monotone pitch across sustained speech)
        if pitch_std < 5.5 and voiced_fraction >= 0.50:
            pitch_score = min((5.5 - pitch_std) / 4.5, 1.0)
            score_components.append(pitch_score * 0.25)
            anomalies.append({
                "type": "MONOTONE_PITCH_ANOMALY",
                "severity": "HIGH" if pitch_std < 2.5 else "MEDIUM",
                "metric_name": "Pitch Variance (σ)",
                "value": f"{round(pitch_std, 1)} Hz",
                "threshold": "< 5.5 Hz (Human normal: 18.0 - 90.0 Hz)",
                "description": "Pitch contour exhibits machine-like uniformity across syllables.",
            })
        else:
            score_components.append(0.0)

        anomaly_score = float(np.clip(np.sum(score_components), 0.0, 1.0))
        confidence = 0.85 if len(valid_idx) >= 15 else 0.55

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": round(confidence, 2),
            "metrics": {
                "pitch_mean_hz": round(pitch_mean, 1),
                "pitch_std_hz": round(pitch_std, 1),
                "jitter": round(jitter, 5),
                "shimmer": round(shimmer, 5),
                "micro_tremor_index": round(micro_tremor_ratio, 4),
                "voiced_fraction": round(voiced_fraction, 2),
            },
            "anomalies_detected": anomalies,
        }
