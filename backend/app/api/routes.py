"""REST API Endpoints for File Uploads, System Configuration, and Diagnostics."""
import os
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
from app.core.config import settings
from app.engine.fusion_scorer import DetectionEngine
from app.audio.decoder import AudioDecoder

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Returns system status and active detection modules."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "sample_rate_hz": settings.SAMPLE_RATE,
        "active_detectors": list(settings.DETECTOR_WEIGHTS.keys()),
        "supported_formats": ["WAV", "MP3", "FLAC", "OGG", "AAC", "MP4", "M4A", "MOV", "WEBM", "MKV"],
        "architecture": "Multi-Domain Feature Fusion + Neural Classifier (ITEGAM-JETIA 2026 & MDPI 2025)",
    }


@router.get("/config")
async def get_configuration() -> Dict[str, Any]:
    """Returns current forensic thresholds and detector weightings."""
    return {
        "sample_rate": settings.SAMPLE_RATE,
        "window_duration_sec": settings.WINDOW_DURATION_SEC,
        "hop_duration_sec": settings.HOP_DURATION_SEC,
        "risk_thresholds": {
            "low": settings.RISK_THRESHOLD_LOW,
            "moderate": settings.RISK_THRESHOLD_MODERATE,
            "high": settings.RISK_THRESHOLD_HIGH,
        },
        "detector_weights": settings.DETECTOR_WEIGHTS,
        "ema_alpha": settings.EMA_ALPHA,
    }


@router.post("/analyze-file")
async def analyze_audio_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Analyzes an uploaded audio or video file (MP4, M4A, WAV, MP3, FLAC, OGG, MOV, WEBM).
    Extracts the audio stream, processes the recording using sliding-window multi-domain
    forensic detectors, and generates a comprehensive forensic report with timeline graphs
    and SHAP domain contributions.
    """
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Decode audio stream from container (supports MP4, M4A, WAV, MP3, FLAC, OGG, etc.)
        try:
            audio_data, total_duration_sec = AudioDecoder.decode_to_16k_mono(
                content=content,
                filename=file.filename or "audio.mp4"
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to extract audio track from {file.filename}: {str(e)}",
            )

        if total_duration_sec < 0.3:
            raise HTTPException(
                status_code=400,
                detail="Audio stream duration is too short for forensic analysis (minimum 0.3s required).",
            )

        # Execute sliding window analysis across entire file
        engine = DetectionEngine()
        window_size = settings.WINDOW_SAMPLES
        hop_size = settings.HOP_SAMPLES

        timeline: List[Dict[str, Any]] = []
        all_anomalies: List[Dict[str, Any]] = []
        domain_shap_accum: Dict[str, List[float]] = {
            "compression": [],
            "acoustic": [],
            "prosody": [],
            "phase": [],
            "emotional": [],
            "statistical_spectral": [],
        }

        # If audio is shorter than window_size, pad with reflection or zero
        if len(audio_data) < window_size:
            pad_width = window_size - len(audio_data)
            audio_padded = np.pad(audio_data, (0, pad_width), mode="constant")
            res = engine.analyze_window(audio_padded, settings.SAMPLE_RATE, window_index=1, timestamp_sec=0.0)
            timeline.append(res)
            all_anomalies.extend(res["diagnostics"])
            for d_k, d_v in res.get("domain_shap_contributions", {}).items():
                if d_k in domain_shap_accum:
                    domain_shap_accum[d_k].append(d_v)
        else:
            window_idx = 0
            for start in range(0, len(audio_data) - window_size + 1, hop_size):
                window_idx += 1
                window = audio_data[start : start + window_size]
                timestamp_sec = start / settings.SAMPLE_RATE
                res = engine.analyze_window(window, settings.SAMPLE_RATE, window_idx, timestamp_sec)
                timeline.append(res)
                all_anomalies.extend(res["diagnostics"])
                for d_k, d_v in res.get("domain_shap_contributions", {}).items():
                    if d_k in domain_shap_accum:
                        domain_shap_accum[d_k].append(d_v)

        # Compute file-level aggregate metrics
        scores = [t["risk_score"] for t in timeline]
        peak_risk = float(np.max(scores)) if scores else 0.0
        avg_risk = float(np.mean(scores)) if scores else 0.0

        # Mean SHAP domain contributions
        domain_shap_mean = {
            k: round(float(np.mean(v)), 3) if v else 0.0
            for k, v in domain_shap_accum.items()
        }

        # Overall verdict formulation (Sustained cluster & distribution analysis)
        high_risk_ratio = float(np.mean([1 if s >= 0.60 else 0 for s in scores])) if scores else 0.0
        moderate_risk_ratio = float(np.mean([1 if s >= 0.35 else 0 for s in scores])) if scores else 0.0

        if avg_risk >= 0.60 or high_risk_ratio >= 0.30:
            overall_verdict = "CRITICAL_AI_CLONE"
            risk_level = "CRITICAL"
        elif avg_risk >= 0.40 or (peak_risk >= 0.65 and high_risk_ratio >= 0.15):
            overall_verdict = "PROBABLE_SYNTHETIC"
            risk_level = "HIGH"
        elif avg_risk >= 0.25 or moderate_risk_ratio >= 0.25:
            overall_verdict = "INCONCLUSIVE_SUSPICIOUS"
            risk_level = "MODERATE"
        else:
            overall_verdict = "GENUINE_HUMAN"
            risk_level = "LOW"

        # Deduplicate anomalies
        unique_anomalies = []
        seen_types = set()
        for a in all_anomalies:
            t = a.get("type")
            if t not in seen_types:
                seen_types.add(t)
                unique_anomalies.append(a)

        latest_recommendation = timeline[-1]["recommendation"] if timeline else ""
        latest_actions = timeline[-1]["suggested_actions"] if timeline else []
        file_ext = os.path.splitext(file.filename or "")[1].upper().replace(".", "")

        return {
            "filename": file.filename,
            "format": file_ext or "AUDIO",
            "duration_seconds": round(total_duration_sec, 2),
            "total_windows_analyzed": len(timeline),
            "overall_verdict": overall_verdict,
            "risk_level": risk_level,
            "average_risk_score": round(avg_risk, 3),
            "peak_risk_score": round(peak_risk, 3),
            "recommendation": latest_recommendation,
            "suggested_actions": latest_actions,
            "domain_shap_contributions": domain_shap_mean,
            "unique_anomalies_detected": unique_anomalies,
            "timeline": timeline,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the file: {str(e)}",
        )
