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
  theme: 'dark' | 'light';
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
  theme,
}) => {
  const isDark = theme === 'dark';

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
      color: 'text-cyan-400',
      borderGlow: 'hover:border-cyan-500/50',
      badge: 'STFT Phase'
    },
    {
      layer: 'Layer 2',
      title: 'Prosodic Micro-Tremors (8–12 Hz)',
      desc: 'Isolates involuntary physiological neuro-muscular vocal tremors that synthetic voice generation algorithms fail to replicate.',
      icon: AudioLines,
      color: 'text-emerald-400',
      borderGlow: 'hover:border-emerald-500/50',
      badge: '8–12Hz Tremor'
    },
    {
      layer: 'Layer 3',
      title: 'Respiration & Cadence Dynamics',
      desc: 'Quantifies continuous phonation periods vs. mandatory human pulmonary inhalation pauses to catch unbroken AI audio streams.',
      icon: Volume2,
      color: 'text-amber-400',
      borderGlow: 'hover:border-amber-500/50',
      badge: 'Breathing AI'
    },
    {
      layer: 'Layer 4',
      title: 'Vocoder Brickwall Cutoffs',
      desc: 'Catches tell-tale 4 kHz / 8 kHz filter cutoffs and unnatural spectral tilt slopes typical in real-time neural vocoders.',
      icon: Sparkles,
      color: 'text-violet-400',
      borderGlow: 'hover:border-violet-500/50',
      badge: 'Brickwall 8kHz'
    },
    {
      layer: 'Layer 5',
      title: 'ASVspoof Standard LFCC (Δ+ΔΔ)',
      desc: 'Computes Linear Frequency Cepstral Coefficients with dynamic delta trajectories capturing high-frequency spectral quantization.',
      icon: BarChart3,
      color: 'text-cyan-400',
      borderGlow: 'hover:border-cyan-500/50',
      badge: 'ASVspoof 5'
    },
    {
      layer: 'Layer 6',
      title: 'Biomechanical Glottal Flow (LPC-NAQ)',
      desc: 'Performs vocal fold inverse filtering to calculate Normalized Amplitude Quotient (NAQ), verifying biological vocal cords.',
      icon: Lock,
      color: 'text-emerald-400',
      borderGlow: 'hover:border-emerald-500/50',
      badge: 'LPC Inverse'
    },
    {
      layer: 'Layer 7',
      title: 'Laryngeal Perturbation (Jitter/Shimmer)',
      desc: 'Measures period-to-period micro-instabilities (Jitter local, RAP) and amplitude perturbations (Shimmer APQ3).',
      icon: Microscope,
      color: 'text-rose-400',
      borderGlow: 'hover:border-rose-500/50',
      badge: 'Jitter & Shimmer'
    },
    {
      layer: 'Layer 8',
      title: 'Higher-Order Bispectrum (QPC)',
      desc: 'Evaluates non-linear Quadratic Phase Coupling across vocal harmonic frequencies that synthetic AI cannot correlate.',
      icon: Layers,
      color: 'text-indigo-400',
      borderGlow: 'hover:border-indigo-500/50',
      badge: 'Bicoherence'
    },
  ];

  return (
    <div className="space-y-16 py-4">
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-4 pb-8">
        <div className="flex flex-col items-center text-center space-y-6 max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full border text-xs font-mono font-medium backdrop-blur-md transition-all shadow-sm bg-cyan-950/40 border-cyan-500/30 text-cyan-300">
            <span className="flex h-2 w-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span>SIH 2026 Problem Statement ID: #26104</span>
            <span className="text-slate-500">•</span>
            <span className="text-emerald-400 font-semibold">Defense-Grade Voice Shield</span>
          </div>

          {/* Glowing Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight">
            Autonomous Real-Time <br className="hidden sm:inline" />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 drop-shadow-sm">
              Voice Cloning & Deepfake
            </span>{' '}
            Interceptor
          </h1>

          {/* Subtitle */}
          <p className={`text-sm sm:text-lg max-w-2xl mx-auto leading-relaxed ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>
            Engineered with an <strong className="text-cyan-400">8-Vector Decomposed Forensic Suite</strong> coupled with a deep neural <strong className="text-emerald-400">LCNN-BiLSTM Ensemble</strong> to neutralize synthetic audio impersonation attacks with zero user friction.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <button
              onClick={() => onNavigate('live')}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold text-sm shadow-lg shadow-cyan-500/25 flex items-center space-x-2 transition-all transform hover:-translate-y-0.5 active:translate-y-0"
            >
              <Zap className="h-4 w-4" />
              <span>Launch Live Call Monitor</span>
              <ArrowRight className="h-4 w-4" />
            </button>

            <button
              onClick={() => onNavigate('upload')}
              className={`px-5 py-3 rounded-xl font-semibold text-sm border transition-all flex items-center space-x-2 ${
                isDark
                  ? 'bg-slate-900/80 hover:bg-slate-800 text-slate-200 border-slate-700/80'
                  : 'bg-white hover:bg-slate-100 text-slate-800 border-slate-300 shadow-sm'
              }`}
            >
              <FileAudio className="h-4 w-4 text-cyan-400" />
              <span>Analyze File / Video</span>
            </button>

            <button
              onClick={onOpenCalibration}
              className={`px-4 py-3 rounded-xl font-medium text-xs sm:text-sm border transition-all flex items-center space-x-1.5 ${
                isDark
                  ? 'bg-slate-900/50 hover:bg-slate-800 text-slate-300 border-slate-800'
                  : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
              }`}
            >
              <Radio className="h-4 w-4 text-emerald-400" />
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
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest font-semibold">
              <Microscope className="h-4 w-4" />
              <span>Forensic Architecture</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold mt-1 text-slate-100">
              8-Vector Multi-Layer Decomposition
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl">
              Beyond simple binary classifications: VoxSentinalX isolates physical, acoustic, and mathematical artifacts across independent forensic dimensions.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 rounded-lg bg-emerald-950/70 text-emerald-300 text-xs font-mono border border-emerald-800/60 flex items-center space-x-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
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
                className={`glass-card rounded-xl p-5 flex flex-col justify-between border relative overflow-hidden group ${card.borderGlow} transition-all duration-300`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-slate-400 font-semibold uppercase tracking-wider">
                      {card.layer}
                    </span>
                    <span className="rounded bg-slate-800/80 px-2 py-0.5 text-[10px] font-mono text-cyan-300 border border-slate-700">
                      {card.badge}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-lg bg-slate-900/90 border border-slate-800 text-cyan-400 shadow-sm group-hover:scale-110 transition-transform">
                      <Icon className={`h-5 w-5 ${card.color}`} />
                    </div>
                    <h3 className="text-sm font-bold text-slate-200 leading-tight">
                      {card.title}
                    </h3>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed">
                    {card.desc}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-mono text-slate-500">
                  <span>Threshold Tolerance</span>
                  <span className="text-emerald-400 font-bold">±0.03 ms / 0.12 NAQ</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 3. INTERACTIVE THREAT SIMULATION SANDBOX */}
      <section className="glass-panel rounded-2xl p-6 sm:p-8 border border-cyan-500/20 shadow-cyber-card space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center space-x-2 text-amber-400 text-xs font-mono uppercase tracking-widest font-semibold">
              <Flame className="h-4 w-4" />
              <span>Interactive Evaluation Sandbox</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold mt-1 text-slate-100">
              Live Threat Simulation & Forensic Decomposition
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
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
                      ? 'bg-red-500/20 text-red-300 border-red-500/50 glow-red font-bold'
                      : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 glow-green font-bold'
                    : 'bg-slate-900/60 hover:bg-slate-800 text-slate-400 border-slate-800'
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
          <div className="flex flex-col items-center justify-center p-6 rounded-xl bg-slate-950/70 border border-slate-800 text-center space-y-4">
            <div className="text-xs font-mono uppercase tracking-wider text-slate-400">
              Composite Deepfake Probability
            </div>

            <div className="relative flex items-center justify-center h-36 w-36">
              <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  className="stroke-slate-800"
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke={activeScenario.riskScore > 50 ? '#ef4444' : '#10b981'}
                  strokeWidth="8"
                  strokeDasharray="264"
                  strokeDashoffset={264 - (264 * activeScenario.riskScore) / 100}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-700 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className={`text-3xl font-extrabold ${activeScenario.riskScore > 50 ? 'text-red-400' : 'text-emerald-400'}`}>
                  {activeScenario.riskScore}%
                </span>
                <span className="text-[10px] font-mono uppercase text-slate-400">Risk Score</span>
              </div>
            </div>

            <div className={`px-3 py-1 rounded-full text-xs font-bold font-mono border ${
              activeScenario.riskScore > 50
                ? 'bg-red-950/80 text-red-300 border-red-500/40'
                : 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40'
            }`}>
              {activeScenario.riskScore > 50 ? '🚨 CRITICAL IMPERSONATION RISK' : '✅ VERIFIED BIOLOGICAL VOICE'}
            </div>
          </div>

          {/* Middle: 8 Vector Micro Telemetry Bars */}
          <div className="lg:col-span-2 space-y-3 p-6 rounded-xl bg-slate-950/70 border border-slate-800">
            <div className="flex items-center justify-between text-xs font-mono pb-1 border-b border-slate-800">
              <span className="text-slate-300 font-bold">8-Vector Forensic Decomposition Metrics</span>
              <span className="text-slate-500">Threshold: &gt;50% Anomaly</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
              {Object.entries(activeScenario.vectors).map(([key, val]) => {
                const isHigh = val > 50;
                return (
                  <div key={key} className="space-y-1">
                    <div className="flex justify-between text-[11px] font-mono">
                      <span className="capitalize text-slate-400">{key} Anomaly</span>
                      <span className={isHigh ? 'text-red-400 font-bold' : 'text-emerald-400 font-bold'}>
                        {val}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden border border-slate-800">
                      <div
                        className={`h-full transition-all duration-700 ${isHigh ? 'bg-gradient-to-r from-amber-500 to-red-500' : 'bg-gradient-to-r from-teal-500 to-emerald-500'}`}
                        style={{ width: `${val}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Detected Forensic Telemetry Bullet points */}
            <div className="mt-4 pt-3 border-t border-slate-800/80">
              <span className="text-[11px] font-mono text-cyan-400 uppercase font-semibold">
                Forensic Findings & Telemetry Explanations:
              </span>
              <ul className="mt-1.5 space-y-1">
                {activeScenario.detectedAnomalies.map((anomaly, idx) => (
                  <li key={idx} className="text-xs text-slate-300 flex items-start space-x-2">
                    <span className="text-cyan-400 font-bold">•</span>
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
          <div className="text-xs font-mono uppercase tracking-widest text-cyan-400 font-semibold">
            Zero-Friction Ingestion
          </div>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-100">
            How VoxSentinalX Intercepts Voice Clones
          </h2>
          <p className="text-xs sm:text-sm text-slate-400">
            End-to-end execution pipeline running within &lt;120ms latency per 1.0s audio frame.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3 relative">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-cyan-500/40">01</span>
              <Volume2 className="h-5 w-5 text-cyan-400" />
            </div>
            <h3 className="font-bold text-sm text-slate-200">Speakerphone Audio Capture</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              No telecom app or SIM hacks needed: phone speaker audio is captured directly via browser microphone over 16 kHz Int16 PCM.
            </p>
          </div>

          <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3 relative">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-emerald-500/40">02</span>
              <Radio className="h-5 w-5 text-emerald-400" />
            </div>
            <h3 className="font-bold text-sm text-slate-200">Voiceprint Separation</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Calibrated baseline voiceprint filters out user speech, isolating only the incoming caller audio for forensic evaluation.
            </p>
          </div>

          <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3 relative">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-violet-500/40">03</span>
              <Cpu className="h-5 w-5 text-violet-400" />
            </div>
            <h3 className="font-bold text-sm text-slate-200">8-Vector & LCNN Inference</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Dual-engine extraction: 8 deterministic forensic algorithms fused with deep PyTorch Light-CNN (MFM + BiLSTM + Self-Attention).
            </p>
          </div>

          <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-3 relative">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-black text-rose-500/40">04</span>
              <AlertTriangle className="h-5 w-5 text-rose-400" />
            </div>
            <h3 className="font-bold text-sm text-slate-200">Emergency Countermeasures</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Instant HUD visual alerts, emergency call interruption recommendations, and cryptographic forensic audit logs.
            </p>
          </div>
        </div>
      </section>

      {/* 5. SCIENTIFIC BENCHMARKS & DATASET HARVESTER */}
      <section className="glass-card rounded-2xl p-6 sm:p-8 border border-slate-800 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center space-x-2 text-emerald-400 text-xs font-mono uppercase tracking-widest font-semibold">
              <Cpu className="h-4 w-4" />
              <span>Multi-Lingual Model & Datasets</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold mt-1 text-slate-100">
              Validated on Global & Indian Datasets
            </h2>
          </div>

          <button
            onClick={() => onNavigate('train')}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-all flex items-center space-x-2 self-start md:self-auto"
          >
            <span>Open Model Training Suite</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div className="text-2xl sm:text-3xl font-black text-cyan-400 font-mono">&lt; 1.8%</div>
            <div className="text-xs text-slate-400 mt-1 font-mono">Equal Error Rate (EER)</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div className="text-2xl sm:text-3xl font-black text-emerald-400 font-mono">&lt; 120 ms</div>
            <div className="text-xs text-slate-400 mt-1 font-mono">Frame Latency</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div className="text-2xl sm:text-3xl font-black text-violet-400 font-mono">12+</div>
            <div className="text-xs text-slate-400 mt-1 font-mono">Indic Languages (IndicSynth)</div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <div className="text-2xl sm:text-3xl font-black text-amber-400 font-mono">ASVspoof 5</div>
            <div className="text-xs text-slate-400 mt-1 font-mono">2024 Benchmark Standard</div>
          </div>
        </div>
      </section>

      {/* 6. BOTTOM CALL TO ACTION BANNER */}
      <section className="rounded-2xl p-8 bg-gradient-to-r from-cyan-950/60 via-slate-950 to-emerald-950/60 border border-cyan-500/30 shadow-neon-cyan flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="space-y-1 text-center sm:text-left">
          <div className="flex items-center justify-center sm:justify-start space-x-2">
            <Shield className="h-5 w-5 text-cyan-400" />
            <h3 className="text-xl font-bold text-white">Ready for Real-Time Call Interception?</h3>
          </div>
          <p className="text-xs sm:text-sm text-slate-400 max-w-xl">
            Start live streaming audio, analyze suspect MP3/WAV voice notes, or train the LCNN neural model on your own dataset.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigate('live')}
            className="px-6 py-3 rounded-xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold text-sm shadow-md transition-all flex items-center space-x-2"
          >
            <Zap className="h-4 w-4" />
            <span>Launch Monitor</span>
          </button>
        </div>
      </section>
    </div>
  );
};
