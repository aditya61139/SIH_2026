export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
export type AlertType = 'NORMAL' | 'CAUTION' | 'WARNING' | 'IMMEDIATE_ACTION_REQUIRED';

export interface AnomalyItem {
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  metric_name: string;
  value: string | number;
  threshold: string;
  description: string;
  source_detector?: string;
}

export interface AnalysisUpdate {
  type?: string;
  window_index: number;
  timestamp: string;
  timestamp_sec: number;
  risk_score: number;
  raw_risk_score: number;
  neural_synthetic_probability?: number;
  is_spike: boolean;
  risk_level: RiskLevel;
  alert_type: AlertType;
  status_text: string;
  user_message: string;
  recommendation: string;
  suggested_actions: string[];
  diagnostics: AnomalyItem[];
  domain_shap_contributions?: {
    compression?: number;
    acoustic?: number;
    prosody?: number;
    phase?: number;
    emotional?: number;
    statistical_spectral?: number;
  };
  layer_scores: {
    compression?: number;
    acoustic?: number;
    prosody?: number;
    spectral?: number;
    phase?: number;
    breathing?: number;
    acoustic_artifacts?: number;
  };
  layer_metrics: Record<string, any>;
  speaker_separation: {
    caller_ratio: number;
    user_ratio: number;
    calibrated: boolean;
  };
}

export interface FileAnalysisReport {
  filename: string;
  format?: string;
  duration_seconds: number;
  total_windows_analyzed: number;
  overall_verdict: string;
  risk_level: RiskLevel;
  average_risk_score: number;
  peak_risk_score: number;
  recommendation: string;
  suggested_actions: string[];
  domain_shap_contributions?: Record<string, number>;
  unique_anomalies_detected: AnomalyItem[];
  timeline: AnalysisUpdate[];
}
