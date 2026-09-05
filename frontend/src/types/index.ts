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

export interface LayerScores {
  spectral: number;
  prosody: number;
  breathing: number;
  acoustic_artifacts: number;
  lfcc: number;
  glottal: number;
  perturbation: number;
  bispectrum: number;
  neural_lcnn: number;
}

export interface AnalysisUpdate {
  type?: string;
  window_index: number;
  timestamp: string;
  timestamp_sec: number;
  risk_score: number;
  raw_risk_score: number;
  is_spike: boolean;
  risk_level: RiskLevel;
  alert_type: AlertType;
  status_text: string;
  user_message: string;
  recommendation: string;
  suggested_actions: string[];
  diagnostics: AnomalyItem[];
  layer_scores: LayerScores;
  layer_metrics: Record<string, Record<string, any>>;
  speaker_separation: {
    caller_ratio: number;
    user_ratio: number;
    calibrated: boolean;
  };
}

export interface FileAnalysisReport {
  filename: string;
  duration_seconds: number;
  total_windows_analyzed: number;
  overall_verdict: string;
  risk_level: RiskLevel;
  average_risk_score: number;
  peak_risk_score: number;
  recommendation: string;
  suggested_actions: string[];
  unique_anomalies_detected: AnomalyItem[];
  timeline: AnalysisUpdate[];
}

export interface DatasetItem {
  name: string;
  description: string;
  url: string;
  type: string;
  installed: boolean;
  sample_count: number;
  local_path: string;
}

export interface ModelMetrics {
  status: string;
  samples_evaluated?: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  equal_error_rate_eer: number;
  confusion_matrix?: {
    true_positives_synthetic: number;
    false_positives: number;
    true_negatives_genuine: number;
    false_negatives: number;
  };
}
