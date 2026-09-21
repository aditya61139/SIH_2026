import React, { useState } from 'react';
import {
  Shield,
  Activity,
  FileAudio,
  Cpu,
  Radio,
  Zap,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  AudioLines,
  Microscope,
  Lock,
  Layers,
  Sparkles,
  BarChart3,
  Flame,
  FileText,
  Volume2
} from 'lucide-react';
import { WaveformHeroVisualizer } from './WaveformHeroVisualizer';

interface LandingViewProps {
  onNavigate: (tab: 'live' | 'upload' | 'train' | 'settings') => void;
  onOpenCalibration: () => void;
}

interface ThreatScenario {
  id: string;
  name: string;
  type: 'fake' | 'real';
  description: string;
  riskScore: number;
  vectors: {
    spectral: number;
    prosody: number;
    breathing: number;
    vocoder: number;
    lfcc: number;
    glottal: number;
    perturbation: number;
    bispectrum: number;
  };
  detectedAnomalies: string[];
}

export const LandingView: React.FC<LandingViewProps> = ({
  onNavigate,
  onOpenCalibration,
}) => {

  const scenarios: ThreatScenario[] = [
    {
      id: 'clone_ceo',
      name: '⚠️ Cloned Executive Wire Fraud (Neural Vocoder)',
      type: 'fake',
      description: 'High-fidelity synthetic clone targeting financial authorization with zero breath pauses and flat phase alignment.',
      riskScore: 92,
      vectors: {
        spectral: 88,
        prosody: 94,
        breathing: 96,
        vocoder: 91,
        lfcc: 89,
        glottal: 85,
        perturbation: 92,
        bispectrum: 95,
      },
      detectedAnomalies: [
        'Missing 8-12 Hz involuntary vocal micro-tremors',
        'Abrupt 8 kHz vocoder brickwall cutoff (HiFi-GAN footprint)',
        '14.2s unbroken phonation without respiratory inhalation',
        'Synthetic STFT phase discontinuity'
      ]
    },
    {
      id: 'real_human',
      name: '✅ Verified Authentic Human Caller',
      type: 'real',
      description: 'Natural human speaker with authentic glottal airflow (NAQ 0.142), organic jitter, and natural breathing cadence.',
      riskScore: 8,
      vectors: {
        spectral: 6,
        prosody: 8,
        breathing: 5,
        vocoder: 9,
        lfcc: 12,
        glottal: 7,
        perturbation: 6,
        bispectrum: 8,
      },
      detectedAnomalies: [
        'Glottal pulse shape aligns with physiological vocal folds',
        'Organic 0.42% period-to-period jitter',
        'Inhalation pauses detected every 3.8s',
        'Harmonic quadratic phase coupling confirmed'
      ]
    },
    {
      id: 'indic_adversarial',
      name: '⚠️ Indic Dialect Voice Clone (IndicSynth Model)',
      type: 'fake',
      description: 'Multi-lingual adversarial clone generating Hindi/Tamil speech with subtle pitch quantization artifacts.',
      riskScore: 84,
      vectors: {
        spectral: 78,
        prosody: 88,
        breathing: 82,
        vocoder: 89,
        lfcc: 86,
        glottal: 81,
        perturbation: 84,
        bispectrum: 80,
      },
      detectedAnomalies: [
        'LFCC delta-delta coefficients reveal Mel-filter quantization',
        'Pitch contour lacks natural physiological micro-intonations',
        'NAQ glottal amplitude quotient outside human baseline'
      ]
    }
  ];

  const [activeScenario, setActiveScenario] = useState<ThreatScenario>(scenarios[0]);

  const forensicCards = [
    {
      layer: 'Layer 1',
      title: 'Spectral & STFT Phase Coherence',
      desc: 'Detects mathematical phase discontinuities and unnatural spectral flatness introduced by Griffin-Lim or neural vocoder synthesis.',
      icon: Activity,
      badge: 'STFT Phase'
    },
    {
      layer: 'Layer 2',
      title: 'Prosodic Micro-Tremors (8–12 Hz)',
      desc: 'Isolates involuntary physiological neuro-muscular vocal tremors that synthetic voice generation algorithms fail to replicate.',
      icon: AudioLines,
      badge: '8–12Hz Tremor'
    },
    {
      layer: 'Layer 3',
      title: 'Respiration & Cadence Dynamics',
      desc: 'Quantifies continuous phonation periods vs. mandatory human pulmonary inhalation pauses to catch unbroken AI audio streams.',
      icon: Volume2,
      badge: 'Breathing AI'
    },
    {
      layer: 'Layer 4',
      title: 'Vocoder Brickwall Cutoffs',
      desc: 'Catches tell-tale 4 kHz / 8 kHz filter cutoffs and unnatural spectral tilt slopes typical in real-time neural vocoders.',
      icon: Sparkles,
      badge: 'Brickwall 8kHz'
    },
    {
      layer: 'Layer 5',
      title: 'ASVspoof Standard LFCC (Δ+ΔΔ)',
      desc: 'Computes Linear Frequency Cepstral Coefficients with dynamic delta trajectories capturing high-frequency spectral quantization.',
      icon: BarChart3,
      badge: 'ASVspoof 5'
    },
    {
      layer: 'Layer 6',
      title: 'Biomechanical Glottal Flow (LPC-NAQ)',
      desc: 'Performs vocal fold inverse filtering to calculate Normalized Amplitude Quotient (NAQ), verifying biological vocal cords.',
      icon: Lock,
      badge: 'LPC Inverse'
    },
    {
      layer: 'Layer 7',
      title: 'Laryngeal Perturbation (Jitter/Shimmer)',
      desc: 'Measures period-to-period micro-instabilities (Jitter local, RAP) and amplitude perturbations (Shimmer APQ3).',
      icon: Microscope,
      badge: 'Jitter & Shimmer'
    },
    {
      layer: 'Layer 8',
      title: 'Higher-Order Bispectrum (QPC)',
      desc: 'Evaluates non-linear Quadratic Phase Coupling across vocal harmonic frequencies that synthetic AI cannot correlate.',
      icon: Layers,
      badge: 'Bicoherence'
    },
  ];

  return (
    <div className="space-y-16 py-4">
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-4 pb-8">
        <div className="flex flex-col items-center text-center space-y-6 max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full border text-xs font-mono font-medium backdrop-blur-md transition-all shadow-xs bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981]">
            <span className="flex h-2 w-2 rounded-full bg-[#10B981] animate-ping"></span>
            <span>SIH 2026 Problem Statement ID: #26104</span>
            <span className="text-[#64748B]">•</span>
            <span className="text-[#10B981] font-bold">Real-Time Voice Forensics</span>
          </div>

          {/* Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white">
            Real-Time Voice Cloning & <br className="hidden sm:inline" />
            <span className="text-[#10B981]">
              Synthetic Audio Detection
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-sm sm:text-lg max-w-2xl mx-auto leading-relaxed text-[#94A3B8]">
            Combines an <strong className="text-[#10B981] font-semibold">8-Vector Forensic Suite</strong> (vocal fold glottal flow, respiration cadence, pitch micro-tremors, and bispectral phase coupling) with a deep neural <strong className="text-[#10B981] font-semibold">Light-CNN Classifier</strong> to identify synthetic speech in real time.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <button
              onClick={() => onNavigate('live')}
              className="px-6 py-3 rounded-xl bg-[#10B981] hover:bg-[#059669] text-[#0D0E11] font-bold text-sm shadow-lg shadow-[#10B981]/25 flex items-center space-x-2 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
            >
              <Zap className="h-4 w-4" />
              <span>Launch Live Call Monitor</span>
              <ArrowRight className="h-4 w-4" />
            </button>

            <button
              onClick={() => onNavigate('upload')}
              className="px-5 py-3 rounded-xl font-semibold text-sm border transition-all flex items-center space-x-2 bg-[#1A1C23] hover:bg-[#15171C] text-white border-[#2A2E37] shadow-xs"
            >
              <FileAudio className="h-4 w-4 text-[#10B981]" />
              <span>Analyze File / Video</span>
            </button>

            <button
              onClick={onOpenCalibration}
              className="px-4 py-3 rounded-xl font-medium text-xs sm:text-sm border transition-all flex items-center space-x-1.5 bg-[#15171C] hover:bg-[#10B981]/10 text-[#E2E8F0] hover:text-[#10B981] border-[#2A2E37]"
            >
              <Radio className="h-4 w-4 text-[#10B981]" />
              <span>Calibrate Voiceprint</span>
            </button>
          </div>
        </div>

        {/* Live Audio Visualizer Canvas */}
        <div className="mt-10 max-w-5xl mx-auto">
          <WaveformHeroVisualizer />
        </div>
      </section>

      {/* 2. 8-VECTOR FORENSIC BENTO MATRIX */}
      <section className="space-y-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b pb-4 border-[#252830]">
          <div>
            <div className="flex items-center space-x-2 text-[#10B981] text-xs font-mono uppercase tracking-widest font-bold">
              <Microscope className="h-4 w-4" />
              <span>Forensic Architecture</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold mt-1 text-white">
              8-Vector Multi-Layer Decomposition
            </h2>
            <p className="text-xs sm:text-sm mt-1 max-w-xl text-[#94A3B8]">
              Beyond simple binary classifications: VoxSentinalX isolates physical, acoustic, and mathematical artifacts across independent forensic dimensions.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 rounded-lg text-xs font-mono border flex items-center space-x-1.5 bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30 font-semibold">
              <CheckCircle2 className="h-3.5 w-3.5 text-[#10B981]" />
              <span>Deep Neural LCNN Fusion Active</span>
            </span>
          </div>
        </div>

        {/* Bento Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {forensicCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div
                key={idx}
                className="rounded-xl p-5 flex flex-col justify-between border transition-all duration-200 hover:-translate-y-0.5 bg-[#1A1C23] border-[#2A2E37] shadow-xl hover:shadow-2xl hover:border-[#374151]"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-[#64748B]">
                      {card.layer}
                    </span>
                    <span className="rounded px-2 py-0.5 text-[10px] font-mono border bg-[#15171C] text-[#10B981] border-[#252830] font-bold">
                      {card.badge}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-lg border shadow-xs bg-[#15171C] text-[#10B981] border-[#2A2E37]">
                      <Icon className="h-5 w-5" />
                    </div>
                    <h3 className="text-sm font-bold leading-tight text-white">
                      {card.title}
                    </h3>
                  </div>

                  <p className="text-xs leading-relaxed text-[#94A3B8]">
                    {card.desc}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t flex items-center justify-between text-[11px] font-mono border-[#252830] text-[#64748B]">
                  <span>Threshold Tolerance</span>
                  <span className="text-[#10B981] font-bold">±0.03 ms / 0.12 NAQ</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 3. INTERACTIVE THREAT SIMULATION SANDBOX */}
      <section className="rounded-2xl p-6 sm:p-8 border space-y-6 bg-[#1A1C23] border-[#2A2E37] shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-4 border-[#252830]">
          <div>
            <div className="flex items-center space-x-2 text-[#10B981] text-xs font-mono uppercase tracking-widest font-bold">
              <Flame className="h-4 w-4" />
              <span>Interactive Evaluation Sandbox</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold mt-1 text-white">
              Live Threat Simulation & Forensic Decomposition
            </h2>
            <p className="text-xs sm:text-sm mt-0.5 text-[#94A3B8]">
              Select a simulated caller profile to test how the 8 forensic vectors respond in real time.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            {scenarios.map((sc) => (
              <button
                key={sc.id}
                onClick={() => setActiveScenario(sc)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                  activeScenario.id === sc.id
                    ? sc.type === 'fake'
                      ? 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/40 font-bold shadow-xs'
                      : 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/40 font-bold shadow-xs'
                    : 'bg-[#15171C] hover:bg-[#1A1C23] text-[#94A3B8] border-[#2A2E37]'
                }`}
              >
                {sc.name.split(' ')[0]} {sc.name.split(' ')[1]}
              </button>
            ))}
          </div>
        </div>

        {/* Interactive Scenario Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
          {/* Left: Score Gauge */}
          <div className="flex flex-col items-center justify-center p-6 rounded-xl border text-center space-y-4 bg-[#15171C] border-[#2A2E37]">
            <div className="text-xs font-mono uppercase tracking-wider text-[#94A3B8]">
              Composite Deepfake Probability
            </div>

            <div className="relative flex items-center justify-center h-36 w-36">
              <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke="#374151"
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke={activeScenario.riskScore > 50 ? '#EF4444' : '#10B981'}
                  strokeWidth="8"
                  strokeDasharray="264"
                  strokeDashoffset={264 - (264 * activeScenario.riskScore) / 100}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-700 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className={`text-3xl font-extrabold ${activeScenario.riskScore > 50 ? 'text-[#EF4444]' : 'text-[#10B981]'}`}>
                  {activeScenario.riskScore}%
                </span>
                <span className="text-[10px] font-mono uppercase text-[#94A3B8]">Risk Score</span>
              </div>
            </div>

            <div className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${
              activeScenario.riskScore > 50
                ? 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30'
                : 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/30'
            }`}>
              {activeScenario.riskScore > 50 ? '🚨 CRITICAL IMPERSONATION RISK' : '✅ VERIFIED BIOLOGICAL VOICE'}
            </div>
          </div>

          {/* Middle: 8 Vector Micro Telemetry Bars */}
          <div className="lg:col-span-2 space-y-3 p-6 rounded-xl border bg-[#15171C] border-[#2A2E37]">
            <div className="flex items-center justify-between text-xs font-mono pb-1 border-b border-[#252830]">
              <span className="font-bold text-white">8-Vector Forensic Decomposition Metrics</span>
              <span className="text-[#64748B]">Threshold: &gt;50% Anomaly</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              {Object.entries(activeScenario.vectors).map(([key, val]) => {
                const isHigh = val > 50;
                return (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-mono">
                      <span className="capitalize text-[#94A3B8]">{key} Anomaly</span>
                      <span className={isHigh ? 'text-[#EF4444] font-bold' : 'text-[#10B981] font-bold'}>
                        {val}%
                      </span>
                    </div>
                    <div className="w-full rounded-full h-1.5 overflow-hidden border bg-[#1A1C23] border-[#252830]">
                      <div
                        className={`h-full transition-all duration-700 ${isHigh ? 'bg-gradient-to-r from-amber-500 to-[#EF4444]' : 'bg-gradient-to-r from-emerald-600 to-[#10B981]'}`}
                        style={{ width: `${val}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Detected Forensic Telemetry Bullet points */}
            <div className="mt-4 pt-3 border-t border-[#252830]">
              <span className="text-[11px] font-mono text-[#10B981] uppercase font-bold">
                Forensic Findings & Telemetry Explanations:
              </span>
              <ul className="mt-1.5 space-y-1">
                {activeScenario.detectedAnomalies.map((anomaly, idx) => (
                  <li key={idx} className="text-xs flex items-start space-x-2 text-[#E2E8F0]">
                    <span className="text-[#10B981] font-bold">•</span>
                    <span>{anomaly}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 4. SYSTEM ARCHITECTURE DATA-FLOW PIPELINE */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <div className="text-xs font-mono uppercase tracking-widest text-[#10B981] font-bold">
            Zero-Friction Ingestion
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            How VoxSentinalX Intercepts Voice Clones
          </h2>
          <p className="text-xs sm:text-sm text-[#94A3B8]">
            End-to-end execution pipeline running within &lt;120ms latency per 1.0s audio frame.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="rounded-xl p-5 border space-y-3 relative transition-all duration-200 hover:-translate-y-0.5 bg-[#1A1C23] border-[#2A2E37] shadow-xl hover:border-[#10B981]/40">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-[#10B981]/25">01</span>
              <Volume2 className="h-5 w-5 text-[#10B981]" />
            </div>
            <h3 className="font-bold text-sm text-white">Speakerphone Audio Capture</h3>
            <p className="text-xs leading-relaxed text-[#94A3B8]">
              No telecom app or SIM hacks needed: phone speaker audio is captured directly via browser microphone over 16 kHz Int16 PCM.
            </p>
          </div>

          <div className="rounded-xl p-5 border space-y-3 relative transition-all duration-200 hover:-translate-y-0.5 bg-[#1A1C23] border-[#2A2E37] shadow-xl hover:border-[#10B981]/40">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-[#10B981]/25">02</span>
              <Radio className="h-5 w-5 text-[#10B981]" />
            </div>
            <h3 className="font-bold text-sm text-white">Voiceprint Separation</h3>
            <p className="text-xs leading-relaxed text-[#94A3B8]">
              Calibrated baseline voiceprint filters out user speech, isolating only the incoming caller audio for forensic evaluation.
            </p>
          </div>

          <div className="rounded-xl p-5 border space-y-3 relative transition-all duration-200 hover:-translate-y-0.5 bg-[#1A1C23] border-[#2A2E37] shadow-xl hover:border-[#10B981]/40">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-[#10B981]/25">03</span>
              <Cpu className="h-5 w-5 text-[#10B981]" />
            </div>
            <h3 className="font-bold text-sm text-white">8-Vector & LCNN Inference</h3>
            <p className="text-xs leading-relaxed text-[#94A3B8]">
              Dual-engine extraction: 8 deterministic forensic algorithms fused with deep PyTorch Light-CNN (MFM + BiLSTM + Self-Attention).
            </p>
          </div>

          <div className="rounded-xl p-5 border space-y-3 relative transition-all duration-200 hover:-translate-y-0.5 bg-[#1A1C23] border-[#2A2E37] shadow-xl hover:border-[#EF4444]/40">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-[#EF4444]/25">04</span>
              <AlertTriangle className="h-5 w-5 text-[#EF4444]" />
            </div>
            <h3 className="font-bold text-sm text-white">Emergency Countermeasures</h3>
            <p className="text-xs leading-relaxed text-[#94A3B8]">
              Instant HUD visual alerts, emergency call interruption recommendations, and cryptographic forensic audit logs.
            </p>
          </div>
        </div>
      </section>

      {/* 5. SCIENTIFIC BENCHMARKS & DATASET HARVESTER */}
      <section className="rounded-2xl p-6 sm:p-8 border space-y-6 bg-[#1A1C23] border-[#2A2E37] shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b pb-4 border-[#252830]">
          <div>
            <div className="flex items-center space-x-2 text-[#10B981] text-xs font-mono uppercase tracking-widest font-bold">
              <Cpu className="h-4 w-4" />
              <span>Multi-Lingual Model & Datasets</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold mt-1 text-white">
              Validated on Global & Indian Datasets
            </h2>
          </div>

          <button
            onClick={() => onNavigate('train')}
            className="px-4 py-2 rounded-xl text-xs font-semibold border transition-all flex items-center space-x-2 self-start md:self-auto bg-[#10B981]/10 hover:bg-[#10B981]/20 text-[#10B981] border-[#10B981]/30"
          >
            <span>Open Model Training Suite</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <div className="p-4 rounded-xl border bg-[#15171C] border-[#2A2E37]">
            <div className="text-2xl sm:text-3xl font-black text-[#10B981] font-mono">6.86%</div>
            <div className="text-xs mt-1 font-mono text-[#94A3B8]">Equal Error Rate (EER)</div>
          </div>

          <div className="p-4 rounded-xl border bg-[#15171C] border-[#2A2E37]">
            <div className="text-2xl sm:text-3xl font-black text-[#10B981] font-mono">86.3%</div>
            <div className="text-xs mt-1 font-mono text-[#94A3B8]">Benchmark Accuracy</div>
          </div>

          <div className="p-4 rounded-xl border bg-[#15171C] border-[#2A2E37]">
            <div className="text-2xl sm:text-3xl font-black font-mono text-white">&lt; 150 ms</div>
            <div className="text-xs mt-1 font-mono text-[#94A3B8]">Pipeline Latency</div>
          </div>

          <div className="p-4 rounded-xl border bg-[#15171C] border-[#2A2E37]">
            <div className="text-2xl sm:text-3xl font-black text-[#10B981] font-mono">5,497</div>
            <div className="text-xs mt-1 font-mono text-[#94A3B8]">Unified Corpus Samples</div>
          </div>
        </div>
      </section>

      {/* 6. BOTTOM CALL TO ACTION BANNER */}
      <section className="rounded-2xl p-8 border flex flex-col sm:flex-row items-center justify-between gap-6 bg-gradient-to-r from-[#1A1C23] via-[#15171C] to-[#1A1C23] border-[#2A2E37] shadow-xl">
        <div className="space-y-1 text-center sm:text-left">
          <div className="flex items-center justify-center sm:justify-start space-x-2">
            <Shield className="h-5 w-5 text-[#10B981]" />
            <h3 className="text-xl font-bold text-white">Ready for Real-Time Call Interception?</h3>
          </div>
          <p className="text-xs sm:text-sm max-w-xl text-[#94A3B8]">
            Start live streaming audio, analyze suspect MP3/WAV voice notes, or train the LCNN neural model on your own dataset.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate('live')}
            className="px-6 py-3 rounded-xl bg-[#10B981] hover:bg-[#059669] text-[#0D0E11] font-bold text-sm shadow-lg shadow-[#10B981]/25 transition-all flex items-center space-x-2"
          >
            <Zap className="h-4 w-4" />
            <span>Launch Monitor</span>
          </button>
        </div>
      </section>
    </div>
  );
};
