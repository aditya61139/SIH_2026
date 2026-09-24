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
  replay_attack: number;
}

export interface LanguageProfile {
  language_family: string;
  estimated_language: string;
  vowel_space_area: number;
  retroflex_dip_ratio: number;
  npvi_rhythm_index: number;
  formant_dispersion?: number;
  multilingual_synthetic_prob?: number;
}

export interface ReplayProfile {
  thd_score: number;
  rt60_ratio: number;
  coloration_score: number;
  dac_transient_score?: number;
  replay_probability: number;
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
  language_profile?: LanguageProfile;
  replay_profile?: ReplayProfile;
  codec_normalization?: {
    codec: string;
    hf_ratio: number;
    compensation_factor: number;
  };
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
  layer_scores?: LayerScores;
  language_profile?: LanguageProfile;
  replay_profile?: ReplayProfile;
  audit_certificate?: any;
  sha256_evidence_hash?: string;
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
