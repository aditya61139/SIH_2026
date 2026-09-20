"""Rule-Based Granular Diagnostic Message and Countermeasure Generator (Comprehensive Suite)."""
from typing import Dict, Any, List


class DiagnosticGenerator:
    """
    Transforms quantitative detector metrics into rich, human-understandable
    diagnostic cards, severity classifications, and actionable security countermeasures.
    """

    @staticmethod
    def generate_report(
        risk_score: float,
        detector_results: Dict[str, Any],
        is_spike: bool = False,
    ) -> Dict[str, Any]:
        """
        Synthesizes all forensic findings into structured diagnostics and actionable guidance.
        """
        # 1. Determine Risk Level
        if risk_score >= 0.80:
            risk_level = "CRITICAL"
            alert_type = "IMMEDIATE_ACTION_REQUIRED"
            status_text = "High probability of AI-generated / cloned voice detected"
        elif risk_score >= 0.60:
            risk_level = "HIGH"
            alert_type = "WARNING"
            status_text = "Significant voice anomalies detected"
        elif risk_score >= 0.30:
            risk_level = "MODERATE"
            alert_type = "CAUTION"
            status_text = "Minor acoustic irregularities observed"
        else:
            risk_level = "LOW"
            alert_type = "NORMAL"
            status_text = "Natural human voice patterns verified"

        # 2. Collect and categorize all individual detector anomalies
        all_anomalies = []
        for det_name, det_res in detector_results.items():
            if isinstance(det_res, dict) and "anomalies_detected" in det_res:
                for anom in det_res["anomalies_detected"]:
                    anom["source_detector"] = det_name
                    all_anomalies.append(anom)

        # 3. Add spike alert if sudden voice characteristics change occurred mid-conversation
        if is_spike:
            all_anomalies.insert(0, {
                "type": "VOICE_SWAP_EVENT",
                "severity": "CRITICAL",
                "metric_name": "Risk Velocity (Δ > 0.28 in < 2s)",
                "value": "Sudden Spike",
                "threshold": "Rapid acoustic profile shift",
                "description": "Voice acoustic profile changed abruptly mid-conversation. Potential dynamic voice clone takeover or switched speaker.",
                "source_detector": "fusion_engine",
            })

        # 4. Formulate Primary User-Facing Message
        if risk_level == "CRITICAL":
            user_message = (
                "Alert: Voice analysis indicates a high likelihood of synthetic speech or voice cloning. "
                "Multiple acoustic and neural feature anomalies were detected."
            )
            recommendation = (
                "High Risk: Avoid authorizing financial transfers, credential releases, or sensitive actions. "
                "Verify the caller's identity through an independent, verified callback."
            )
            suggested_actions = [
                "Ask unpredictable challenge questions known only to the real contact",
                "Hang up and call back on a verified direct phone number",
                "Request secondary verification via corporate email or messaging channel",
                "Save forensic telemetry log for security review",
            ]
        elif risk_level == "HIGH":
            user_message = (
                "Warning: This voice exhibits artificial characteristics such as unnatural pitch stability or spectral discontinuities. "
                "Verify the caller's identity before continuing."
            )
            recommendation = (
                "Caution: Acoustic patterns are inconsistent with natural human speech dynamics. "
                "Treat requests with skepticism."
            )
            suggested_actions = [
                "Ask a personal challenge question",
                "Confirm request through a secondary communication channel",
                "Do not share confidential organizational or financial details",
            ]
        elif risk_level == "MODERATE":
            user_message = (
                "Caution: Minor acoustic irregularities observed. This can result from cellular compression, poor network signal, or low-bitrate codecs."
            )
            recommendation = (
                "Continue monitoring the call. For sensitive transactions, confirm identity through standard channels."
            )
            suggested_actions = [
                "Continue monitoring live telemetry",
                "Ask the caller to repeat if audio quality is degraded",
            ]
        else:
            user_message = "Natural voice verified: Pitch variation, respiratory cadence, and spectral resonance match authentic human speech."
            recommendation = "No synthetic impersonation indicators detected. Routine monitoring active."
            suggested_actions = [
                "Acoustic characteristics appear consistent with natural speech",
            ]

        return {
            "risk_level": risk_level,
            "alert_type": alert_type,
            "status_text": status_text,
            "user_message": user_message,
            "recommendation": recommendation,
            "suggested_actions": suggested_actions,
            "anomalies": all_anomalies,
        }
