"""Compression Artifact Anomaly Detector (Domain 1).
Based on: Chhatriwala et al., 'A Multi-Domain Feature Framework for Robust Deepfake Audio Detection' (ITEGAM-JETIA, 2026).
"""
import numpy as np
from typing import Dict, Any, List
from app.detectors.base import BaseDetector
from app.audio.codec_simulator import CodecSimulator
from app.audio.preprocessor import AudioPreprocessor


class CompressionDetector(BaseDetector):
    """
    Analyzes codec compression response (Mel-band Delta_k energy deviation).
    Identifies quantization distortions and unnatural spectral irregularity in synthetic speech.
    """

    def __init__(self, sample_rate: int = 16000):
        self.codec_sim = CodecSimulator(n_mels=40, sample_rate=sample_rate)

    @property
    def name(self) -> str:
        return "compression"

    def analyze(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        if len(audio) < sample_rate * 0.1 or AudioPreprocessor.is_silent(audio):
            return {
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "metrics": {
                    "delta_mean": 0.0,
                    "delta_var": 0.0,
                    "distortion_irregularity": 0.0,
                },
                "anomalies_detected": [],
            }

        res = self.codec_sim.extract_compression_features(audio)
        anomalies = []

        # Check for high variance in compression energy delta (Empirically Calibrated on Dataset)
        if res["delta_var"] > 0.185 or res["distortion_irregularity"] > 0.170:
            severity = "CRITICAL" if res["delta_var"] > 0.230 else "HIGH"
            anomalies.append({
                "type": "CODEC_QUANTIZATION_ANOMALY",
                "severity": severity,
                "metric_name": "Compression Distortion Delta (Δk)",
                "value": f"Var={res['delta_var']}, Irreg={res['distortion_irregularity']}",
                "threshold": "Var < 0.185, Irreg < 0.170 (Dataset Calibrated)",
                "description": "Unnatural Mel-band energy deviation under codec compression beyond natural acoustic dynamic range. Characteristic of vocoders lacking psychoacoustic micro-redundancy.",
            })

        return {
            "anomaly_score": res["anomaly_score"],
            "confidence": 0.90,
            "metrics": {
                "delta_mean": res["delta_mean"],
                "delta_var": res["delta_var"],
                "delta_skew": res["delta_skew"],
                "distortion_irregularity": res["distortion_irregularity"],
            },
            "anomalies_detected": anomalies,
        }
