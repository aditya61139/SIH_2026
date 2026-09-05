"""Multi-Domain Fusion Scorer and Real-Time Detection Engine.
Integrates the 6-Domain Feature Framework (Chhatriwala et al., 2026) and
Cross-Attention Feature Extraction (Gong & Li, 2025).
"""
import numpy as np
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.detectors.multidomain_extractor import MultiDomainFeatureExtractor
from app.detectors.neural_classifier import MultiDomainNeuralClassifier
from app.detectors.compression_detector import CompressionDetector
from app.detectors.spectral_detector import SpectralDetector
from app.detectors.prosody_detector import ProsodyDetector
from app.detectors.breathing_detector import BreathingDetector
from app.detectors.acoustic_artifacts import AcousticArtifactDetector
from app.audio.speaker_separator import SpeakerSeparator
from app.audio.preprocessor import AudioPreprocessor
from app.engine.diagnostic_generator import DiagnosticGenerator


class DetectionEngine:
    """
    Orchestrates the 6-Domain Feature Extraction Pipeline,
    Multi-Domain Neural Classification, and Dynamic Diagnostic Generation.
    """

    def __init__(self):
        self.multidomain_extractor = MultiDomainFeatureExtractor(sample_rate=settings.SAMPLE_RATE)
        self.neural_classifier = MultiDomainNeuralClassifier()
        self.compression_detector = CompressionDetector(sample_rate=settings.SAMPLE_RATE)
        self.spectral_detector = SpectralDetector()
        self.prosody_detector = ProsodyDetector()
        self.breathing_detector = BreathingDetector()
        self.acoustic_detector = AcousticArtifactDetector()
        self.speaker_separator = SpeakerSeparator()

        self.history_scores: List[float] = []
        self.current_ema_score: float = 0.0
        self.total_windows_processed: int = 0

    def analyze_window(
        self,
        audio_window: np.ndarray,
        sample_rate: int = settings.SAMPLE_RATE,
        window_index: int = 0,
        timestamp_sec: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Executes multi-domain forensic analysis on a 2.0-second audio window.
        """
        self.total_windows_processed += 1

        # 1. Separate Caller Audio from User Audio (Speakerphone mode)
        caller_audio, separation_info = self.speaker_separator.isolate_caller_audio(
            audio_window, sample_rate=sample_rate
        )

        formatted_time = f"{int(timestamp_sec // 60):02d}:{int(timestamp_sec % 60):02d}"

        # ── Silence & Inactive Speech Handling (Fast Decay to 0% Risk) ──
        if len(caller_audio) < sample_rate * 0.1 or AudioPreprocessor.is_silent(caller_audio, rms_threshold=0.005):
            # When speech stops / silence is detected, decay risk score aggressively
            self.current_ema_score = max(0.0, float(self.current_ema_score * 0.45 - 0.02))
            if self.current_ema_score < 0.04:
                self.current_ema_score = 0.0
            self.history_scores.append(self.current_ema_score)

            return {
                "window_index": window_index,
                "timestamp": formatted_time,
                "timestamp_sec": round(timestamp_sec, 2),
                "risk_score": round(self.current_ema_score, 3),
                "raw_risk_score": 0.0,
                "neural_synthetic_probability": 0.0,
                "is_spike": False,
                "risk_level": "LOW",
                "alert_type": "NORMAL",
                "status_text": "Ambient Room / Silence (Listening...)",
                "user_message": "Channel is clear. No active speech detected.",
                "recommendation": "Maintain standard security protocol during call pauses.",
                "suggested_actions": ["Awaiting incoming voice stream..."],
                "diagnostics": [],
                "domain_shap_contributions": {
                    "compression": 0.25,
                    "acoustic": 0.20,
                    "prosody": 0.20,
                    "phase": 0.15,
                    "emotional": 0.10,
                    "statistical_spectral": 0.10,
                },
                "layer_scores": {
                    "compression": 0.0,
                    "acoustic": 0.0,
                    "prosody": 0.0,
                    "spectral": 0.0,
                    "phase": 0.0,
                    "breathing": 0.0,
                    "acoustic_artifacts": 0.0,
                },
                "layer_metrics": {
                    "compression": {"delta_mean": 0.0, "delta_var": 0.0},
                    "acoustic": {"mfcc_mean_norm": 0.0, "delta_var_norm": 0.0},
                    "prosody": {"pitch_mean_hz": 0.0, "jitter": 0.0, "shimmer": 0.0},
                    "spectral": {"spectral_flatness": 0.0, "spectral_entropy": 0.0},
                    "phase": {"group_delay_var": 0.0},
                    "breathing": {"continuous_speech_sec": 0.0},
                    "acoustic_artifacts": {"brickwall_cutoff_detected": False},
                },
                "speaker_separation": separation_info,
            }

        # 2. Extract Complete 6-Domain Multi-Feature Representation (Chhatriwala et al. 2026)
        multi_features = self.multidomain_extractor.extract_all(caller_audio)
        fused_vector = multi_features["fused_vector"]

        # 3. Neural Classifier Inference (P(Synthetic) + SHAP Domain Contributions)
        p_genuine, p_synthetic, domain_shap = self.neural_classifier.predict_proba(fused_vector)

        # 4. Individual Modular Detectors for Granular Diagnostics
        comp_res = self.compression_detector.analyze(caller_audio, sample_rate)
        spectral_res = self.spectral_detector.analyze(caller_audio, sample_rate)
        prosody_res = self.prosody_detector.analyze(caller_audio, sample_rate)
        breathing_res = self.breathing_detector.analyze(caller_audio, sample_rate)
        acoustic_res = self.acoustic_detector.analyze(caller_audio, sample_rate)

        detector_results = {
            "compression": comp_res,
            "acoustic": {
                "anomaly_score": multi_features["acoustic"]["anomaly_score"],
                "metrics": multi_features["acoustic"],
                "anomalies_detected": [
                    {
                        "type": "ACOUSTIC_FORMANT_QUANTIZATION",
                        "severity": "HIGH",
                        "metric_name": "MFCC Delta Dynamic Variance",
                        "value": f"Δ-Var: {multi_features['acoustic']['delta_var_norm']}",
                        "threshold": "> 0.50 (Normal human dynamic range)",
                        "description": "Acoustic formant velocity trajectory shows reduced variance typical of neural speech synthesis.",
                    }
                ] if multi_features["acoustic"]["anomaly_score"] > 0.65 else [],
            },
            "prosody": prosody_res,
            "spectral": spectral_res,
            "breathing": breathing_res,
            "acoustic_artifacts": acoustic_res,
        }

        # 5. Hybrid Fusion Score Calculation:
        # Fuses Neural Posterior (60% weight) + Multi-Domain Heuristic Aggregate (40% weight)
        weights = settings.DETECTOR_WEIGHTS
        heuristic_score = (
            weights["compression"] * comp_res["anomaly_score"]
            + weights["acoustic"] * multi_features["acoustic"]["anomaly_score"]
            + weights["prosody"] * prosody_res["anomaly_score"]
            + weights["spectral"] * spectral_res["anomaly_score"]
            + weights["breathing"] * breathing_res["anomaly_score"]
            + weights["acoustic_artifacts"] * acoustic_res["anomaly_score"]
        )

        # Corroboration for heuristic score
        other_heuristic_scores = [
            multi_features["acoustic"]["anomaly_score"],
            prosody_res["anomaly_score"],
            spectral_res["anomaly_score"],
            breathing_res["anomaly_score"],
            acoustic_res["anomaly_score"],
        ]
        if comp_res["anomaly_score"] > 0.30 and max(other_heuristic_scores) < 0.20:
            # Isolated telephony compression artifact
            heuristic_score = min(heuristic_score, 0.15)

        raw_score = 0.60 * p_synthetic + 0.40 * heuristic_score
        raw_score = float(np.clip(raw_score, 0.0, 1.0))

        # 6. Temporal Smoothing (Exponential Moving Average)
        alpha = settings.EMA_ALPHA
        if len(self.history_scores) == 0:
            smoothed_score = raw_score
        else:
            smoothed_score = alpha * raw_score + (1.0 - alpha) * self.current_ema_score

        # Check for sudden risk velocity spike (Voice Swap / Takeover Detection)
        # Only triggers when transitioning into high synthetic clone territory (raw_score >= 0.60)
        prev_score = self.current_ema_score if len(self.history_scores) > 0 else 0.0
        is_spike = (raw_score - prev_score) >= settings.SPIKE_DELTA_THRESHOLD and raw_score >= 0.60

        self.current_ema_score = smoothed_score
        self.history_scores.append(smoothed_score)

        # 7. Generate Rich Diagnostic Report & Actionable Countermeasures
        diagnostic_report = DiagnosticGenerator.generate_report(
            risk_score=smoothed_score,
            detector_results=detector_results,
            is_spike=is_spike,
            shap_contributions=domain_shap,
        )

        formatted_time = f"{int(timestamp_sec // 60):02d}:{int(timestamp_sec % 60):02d}"

        return {
            "window_index": window_index,
            "timestamp": formatted_time,
            "timestamp_sec": round(timestamp_sec, 2),
            "risk_score": round(smoothed_score, 3),
            "raw_risk_score": round(raw_score, 3),
            "neural_synthetic_probability": round(p_synthetic, 3),
            "is_spike": is_spike,
            "risk_level": diagnostic_report["risk_level"],
            "alert_type": diagnostic_report["alert_type"],
            "status_text": diagnostic_report["status_text"],
            "user_message": diagnostic_report["user_message"],
            "recommendation": diagnostic_report["recommendation"],
            "suggested_actions": diagnostic_report["suggested_actions"],
            "diagnostics": diagnostic_report["anomalies"],
            "domain_shap_contributions": domain_shap,
            "layer_scores": {
                "compression": comp_res["anomaly_score"],
                "acoustic": multi_features["acoustic"]["anomaly_score"],
                "prosody": prosody_res["anomaly_score"],
                "spectral": spectral_res["anomaly_score"],
                "phase": multi_features["phase"]["anomaly_score"],
                "breathing": breathing_res["anomaly_score"],
                "acoustic_artifacts": acoustic_res["anomaly_score"],
            },
            "layer_metrics": {
                "compression": comp_res["metrics"],
                "acoustic": multi_features["acoustic"],
                "prosody": prosody_res["metrics"],
                "spectral": spectral_res["metrics"],
                "phase": multi_features["phase"],
                "breathing": breathing_res["metrics"],
                "acoustic_artifacts": acoustic_res["metrics"],
            },
            "speaker_separation": separation_info,
        }

    def reset(self) -> None:
        """Resets engine history and detector states for a new call."""
        self.history_scores.clear()
        self.current_ema_score = 0.0
        self.total_windows_processed = 0
        self.breathing_detector.reset()
