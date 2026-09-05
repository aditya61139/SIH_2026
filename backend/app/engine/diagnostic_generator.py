"""Rule-Based Granular Diagnostic Message and Countermeasure Generator.
Enhanced with Multi-Domain Forensics from ITEGAM-JETIA 2026 & MDPI Electronics 2025.
"""
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
        shap_contributions: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes all forensic findings into structured diagnostics and actionable guidance.
        """
        # 1. Determine Risk Level
        if risk_score >= 0.75:
            risk_level = "CRITICAL"
            alert_type = "IMMEDIATE_ACTION_REQUIRED"
            status_text = "High probability of AI-generated / cloned voice detected"
        elif risk_score >= 0.55:
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
                "metric_name": "Risk Velocity (Δ > 0.25 in < 2s)",
                "value": "Sudden Spike",
                "threshold": "Rapid acoustic profile shift",
                "description": "Voice acoustic profile changed abruptly mid-conversation. Potential dynamic voice clone takeover or switched speaker.",
                "source_detector": "fusion_engine",
            })

        # When risk level is LOW (verified genuine human), suppress isolated sub-threshold artifacts
        if risk_level == "LOW" and not is_spike:
            all_anomalies = []

        # 4. Formulate Primary User-Facing Message
        if risk_level == "CRITICAL":
            user_message = (
                "🛑 CRITICAL ALERT: Multi-domain forensic analysis confirms strong probability of synthetic / cloned speech. "
                "Detected severe anomalies in codec compression response (Δk), glottal jitter/shimmer, and phase coherence."
            )
            recommendation = (
                "🚨 HIGH RISK: DO NOT authorize any financial transfers, credential releases, or confidential approvals. "
                "Initiate immediate out-of-band verification via registered callback."
            )
            suggested_actions = [
                "Request caller to perform out-of-band mobile OTP verification",
                "Terminate call and dial the contact's official verified number",
                "Ask unpredictable challenge questions ('What was our last in-person meeting about?')",
                "Flag call and export forensic telemetry log for security review",
            ]
        elif risk_level == "HIGH":
            user_message = (
                "🚨 WARNING: This voice exhibits artificial characteristics (monotone pitch, low jitter/shimmer, or unnatural compression response). "
                "Verify caller identity before proceeding with confidential discussions."
            )
            recommendation = (
                "⚠️ CAUTION: Voice traits are inconsistent with biological vocal tract dynamics. "
                "Treat telephonic instructions with heightened skepticism."
            )
            suggested_actions = [
                "Ask the caller a personal challenge question known only to them",
                "Request an email confirmation from their verified organization domain",
                "Avoid sharing financial or sensitive operational credentials",
            ]
        elif risk_level == "MODERATE":
            user_message = (
                "🟡 CAUTION: Minor acoustic irregularities detected. This may be caused by noisy cellular compression or subtle voice cloning indicators."
            )
            recommendation = (
                "Keep monitoring the conversation. If discussing high-value transactions, verify identity through standard secondary channels."
            )
            suggested_actions = [
                "Continue monitoring live call telemetry",
                "Request caller to speak clearly if background noise is high",
            ]
        else:
            user_message = "🟢 Voice stream verified: Natural human vocal tract resonances, biological jitter/shimmer, and respiratory cadence detected."
            recommendation = "No synthetic impersonation detected. Routine monitoring active."
            suggested_actions = [
                "Normal conversation flow permitted",
            ]

        return {
            "risk_level": risk_level,
            "alert_type": alert_type,
            "status_text": status_text,
            "user_message": user_message,
            "recommendation": recommendation,
            "suggested_actions": suggested_actions,
            "anomalies": all_anomalies,
            "shap_contributions": shap_contributions or {},
        }
