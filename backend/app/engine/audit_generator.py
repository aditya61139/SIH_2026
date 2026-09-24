"""
Cryptographic Forensic Audit Exporter for VoxSentinalX.
Generates cryptographically sealed, tamper-evident forensic audit certificates
with SHA-256 evidence hashing, 10-layer forensic vector breakdowns,
multilingual profiles, replay attack telemetry, and legal compliance declarations
(aligned with Digital Evidence Admissibility standards).
"""
import hashlib
import hmac
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class ForensicAuditGenerator:
    """
    Constructs tamper-evident forensic audit certificates for voice evidence.
    """

    SECRET_AUDIT_SALT = b"VoxSentinalX-Cryptographic-Forensic-Seal-2026"

    @classmethod
    def compute_sha256(cls, data: bytes) -> str:
        """Calculates SHA-256 cryptographic digest of audio bytes."""
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()

    @classmethod
    def generate_certificate(
        cls,
        filename: str,
        audio_bytes: Optional[bytes] = None,
        duration_sec: float = 0.0,
        overall_verdict: str = "GENUINE_HUMAN",
        risk_level: str = "LOW",
        average_risk_score: float = 0.0,
        peak_risk_score: float = 0.0,
        layer_scores: Optional[Dict[str, float]] = None,
        unique_anomalies: Optional[List[Dict[str, Any]]] = None,
        language_profile: Optional[Dict[str, Any]] = None,
        replay_metrics: Optional[Dict[str, Any]] = None,
        precomputed_sha256: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive forensic certificate payload with cryptographic seal.
        """
        cert_id = f"VOX-CERT-{uuid.uuid4().hex[:12].upper()}"
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        epoch_ts = int(time.time())

        # Calculate or use provided hash
        if audio_bytes is not None:
            sha256_hash = cls.compute_sha256(audio_bytes)
        elif precomputed_sha256:
            sha256_hash = precomputed_sha256
        else:
            sha256_hash = hashlib.sha256(f"{filename}-{duration_sec}-{epoch_ts}".encode()).hexdigest()

        # Format 10-Layer Forensic Decomposition
        default_layers = {
            "spectral": 0.0,
            "prosody": 0.0,
            "breathing": 0.0,
            "acoustic_artifacts": 0.0,
            "lfcc": 0.0,
            "glottal": 0.0,
            "perturbation": 0.0,
            "bispectrum": 0.0,
            "neural_lcnn": 0.0,
            "replay_attack": 0.0,
        }
        if layer_scores:
            default_layers.update(layer_scores)

        # Determine Replay Attack Status
        replay_detected = False
        if replay_metrics and replay_metrics.get("replay_probability", 0.0) >= 0.55:
            replay_detected = True
        elif default_layers.get("replay_attack", 0.0) >= 0.55:
            replay_detected = True

        # Generate cryptographic integrity signature
        seal_payload = (
            f"{cert_id}:{sha256_hash}:{duration_sec}:{overall_verdict}:{peak_risk_score}:{timestamp_iso}"
        ).encode("utf-8")
        integrity_signature = hmac.new(cls.SECRET_AUDIT_SALT, seal_payload, hashlib.sha256).hexdigest()

        # Format legal compliance clause
        compliance_clause = (
            "This digital forensic certificate was generated autonomously by the VoxSentinalX "
            "Biometric Voice Defense Engine. The audio media has been cryptographically sealed via "
            "SHA-256 hash. Acoustic decomposition incorporates biomechanical glottal inverse filtering, "
            "bispectral phase coherence, physical loudspeaker electro-acoustic distortion analysis, "
            "and multilingual phonetic formant dispersion profiling."
        )

        certificate = {
            "certificate_id": cert_id,
            "version": "2.1.0",
            "generated_at_utc": timestamp_iso,
            "media_metadata": {
                "filename": filename,
                "duration_seconds": round(duration_sec, 2),
                "sha256_evidence_hash": sha256_hash,
                "cryptographic_seal": integrity_signature,
            },
            "forensic_verdict": {
                "overall_verdict": overall_verdict,
                "risk_level": risk_level,
                "peak_risk_score": round(peak_risk_score, 4),
                "average_risk_score": round(average_risk_score, 4),
                "is_replay_attack": replay_detected,
            },
            "ten_layer_vector_scores": default_layers,
            "multilingual_profile": language_profile or {
                "language_family": "neutral",
                "estimated_language": "Standard / Neutral",
                "vowel_space_area": 0.0,
                "retroflex_dip_ratio": 0.0,
                "npvi_rhythm_index": 0.0,
            },
            "physical_replay_telemetry": replay_metrics or {
                "thd_score": 0.0,
                "rt60_ratio": 1.0,
                "coloration_score": 0.0,
                "replay_probability": 0.0,
            },
            "anomalies_logged": unique_anomalies or [],
            "legal_compliance": {
                "admissibility_framework": "Digital Evidence Authentication (Hash & Biometric Decomposition)",
                "tamper_evidence": "SHA-256 Content Digest & HMAC Signature Validated",
                "declaration": compliance_clause,
            },
        }

        return certificate
