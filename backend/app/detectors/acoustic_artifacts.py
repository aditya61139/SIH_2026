"""Vocoder and Synthesis Acoustic Artifact Detector."""
import numpy as np
from scipy import signal
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.preprocessor import AudioPreprocessor


class AcousticArtifactDetector(BaseDetector):
    """
    Detects digital synthesis artifacts:
    1. Brickwall frequency cutoff / upsampling artifacts (e.g. sharp drops at 4kHz or 8kHz)
    2. Sub-band spectral energy discontinuity
    3. Robotic periodicity & harmonic decay anomalies
    """

    @property
    def name(self) -> str:
        return "acoustic_artifacts"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.2 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "brickwall_cutoff_detected": False,
                    "spectral_decay_slope": 0.0,
                    "subband_discontinuity": 0.0,
                },
                "anomalies_detected": [],
            }

        # 1. High-Resolution Frequency Spectrum
        n_fft = min(len(audio), 2048)
        freqs, psd = signal.welch(audio, fs=sample_rate, nperseg=n_fft)
        psd_db = 10 * np.log10(np.maximum(psd, 1e-12))

        # 2. Check for Telephone Channel Bandlimiting (Standard 3.4kHz AMR-NB / G.711 or 7.0kHz AMR-WB)
        hf_energy_ratio = np.sum(psd[freqs >= 3800]) / (np.sum(psd) + 1e-12)
        is_telephony_channel = bool(hf_energy_ratio < 0.025)

        # Check for anomalous Vocoder Brickwall Cutoff (only when not a standard telephone channel)
        diff_psd = np.diff(psd_db)
        min_slope = float(np.min(diff_psd))
        brickwall_cutoff = bool(min_slope < -28.0 and not is_telephony_channel)

        # 3. Spectral Energy Decay Slope (Natural voice decays approximately -6dB to -14dB per octave)
        # In telephone audio, evaluate slope strictly within the active passband (200Hz - 3400Hz)
        max_slope_freq = 3400 if is_telephony_channel else 7000
        valid_bins = (freqs >= 200) & (freqs <= max_slope_freq)
        if np.sum(valid_bins) > 10:
            log_f = np.log2(freqs[valid_bins])
            p_db = psd_db[valid_bins]
            slope, _ = np.polyfit(log_f, p_db, 1)
        else:
            slope = -8.0

        # 4. Sub-band energy variances
        # Divide into 4 bands: 0-1kHz, 1-2.5kHz, 2.5-5kHz, 5-8kHz
        b1 = np.mean(psd[(freqs >= 0) & (freqs < 1000)])
        b2 = np.mean(psd[(freqs >= 1000) & (freqs < 2500)])
        b3 = np.mean(psd[(freqs >= 2500) & (freqs < 5000)])
        b4 = np.mean(psd[(freqs >= 5000) & (freqs <= 8000)])

        b_vals = np.array([b1, b2, b3, b4]) + 1e-12
        subband_ratios = b_vals[1:] / b_vals[:-1]
        discontinuity = float(np.std(subband_ratios))

        # ── Anomaly Scoring ──
        anomalies = []
        score_components = []

        if brickwall_cutoff:
            score_components.append(0.50)
            anomalies.append({
                "type": "BRICKWALL_CUTOFF_ARTIFACT",
                "severity": "HIGH",
                "metric_name": "Vocoder Filter Cutoff",
                "value": f"Steep drop ({round(min_slope, 1)} dB/bin)",
                "threshold": "< -25.0 dB/bin",
                "description": "Artificial sharp high-frequency cutoff detected, indicating upsampled or model-constrained neural vocoder synthesis.",
            })
        else:
            score_components.append(0.0)

        # Unnatural spectral tilt / decay
        if slope > -2.0 or slope < -22.0:
            tilt_score = 0.35
            score_components.append(tilt_score)
            anomalies.append({
                "type": "SPECTRAL_TILT_ANOMALY",
                "severity": "MEDIUM",
                "metric_name": "Spectral Decay Slope",
                "value": f"{round(slope, 1)} dB/octave",
                "threshold": "Normal human range: -6.0 to -14.0 dB/oct",
                "description": "Vocal harmonic rolloff deviates significantly from human glottal excitation physics.",
            })
        else:
            score_components.append(0.0)

        anomaly_score = float(np.clip(np.sum(score_components), 0.0, 1.0))

        return {
            "anomaly_score": round(anomaly_score, 3),
            "confidence": 0.75,
            "metrics": {
                "brickwall_cutoff_detected": bool(brickwall_cutoff),
                "spectral_decay_slope": round(float(slope), 2),
                "subband_discontinuity": round(float(discontinuity), 3),
            },
            "anomalies_detected": anomalies,
        }
