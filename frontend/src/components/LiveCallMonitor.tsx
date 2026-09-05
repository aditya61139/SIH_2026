import React, { useState, useEffect, useRef } from 'react';
import { Play, Square, Mic, Volume2, ShieldCheck, UserCheck, Layers, Radio, Radar } from 'lucide-react';
import { VoxSentinalAudioCapture } from '../lib/audioCapture';
import { CanvasAudioVisualizer } from '../lib/audioVisualizer';
import { RiskGauge } from './RiskGauge';
import { DiagnosticFeed } from './DiagnosticFeed';
import { AlertOverlay } from './AlertOverlay';
import { ForensicRadar } from './ForensicRadar';
import { AnalysisUpdate } from '../types';

interface LiveCallMonitorProps {
  captureEngine: VoxSentinalAudioCapture;
  wsUrl: string;
  onOpenCalibration: () => void;
}

export const LiveCallMonitor: React.FC<LiveCallMonitorProps> = ({
  captureEngine,
  wsUrl,
  onOpenCalibration,
}) => {
  const [isMonitoring, setIsMonitoring] = useState<boolean>(false);
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [latestAnalysis, setLatestAnalysis] = useState<AnalysisUpdate | null>(null);
  const [connStatus, setConnStatus] = useState<string>('disconnected');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showAlertModal, setShowAlertModal] = useState<boolean>(false);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const visualizerRef = useRef<CanvasAudioVisualizer | null>(null);

  const handleToggleMonitoring = async () => {
    if (isMonitoring) {
      captureEngine.stopMonitoring();
      setIsMonitoring(false);
      setAudioLevel(0);
      visualizerRef.current?.stop();
      setConnStatus('disconnected');
    } else {
      setErrorMessage(null);
      await captureEngine.startMonitoring(
        wsUrl,
        (data: AnalysisUpdate) => {
          setLatestAnalysis(data);
          visualizerRef.current?.setRiskLevel(data.risk_level);

          if (data.risk_level === 'CRITICAL') {
            setShowAlertModal(true);
          }
        },
        (status, err) => {
          setConnStatus(status);
          if (status === 'connected') {
            setIsMonitoring(true);
            if (canvasRef.current && captureEngine.getAnalyserNode()) {
              visualizerRef.current = new CanvasAudioVisualizer(
                canvasRef.current,
                captureEngine.getAnalyserNode()!
              );
              visualizerRef.current.start();
            }
          } else if (status === 'error') {
            setIsMonitoring(false);
            setErrorMessage(err || 'Failed to connect to stream.');
          } else if (status === 'disconnected') {
            setIsMonitoring(false);
            visualizerRef.current?.stop();
          }
        },
        (level) => {
          setAudioLevel(level);
        }
      );
    }
  };

  useEffect(() => {
    return () => {
      captureEngine.stopMonitoring();
      visualizerRef.current?.stop();
    };
  }, [captureEngine]);

  const riskScore = latestAnalysis?.risk_score ?? 0;
  const riskLevel = latestAnalysis?.risk_level ?? 'LOW';
  const isSpike = latestAnalysis?.is_spike ?? false;
  const diagnostics = latestAnalysis?.diagnostics ?? [];
  const layerScores = latestAnalysis?.layer_scores ?? {
    spectral: 0,
    prosody: 0,
    breathing: 0,
    acoustic_artifacts: 0,
    lfcc: 0,
    glottal: 0,
    perturbation: 0,
    bispectrum: 0,
    neural_lcnn: 0,
  };
  const separation = latestAnalysis?.speaker_separation ?? {
    caller_ratio: 1.0,
    user_ratio: 0.0,
    calibrated: false,
  };

  return (
    <div className="space-y-6">
      {/* Alert Overlay Popup */}
      <AlertOverlay
        isOpen={showAlertModal}
        onClose={() => setShowAlertModal(false)}
        riskScore={riskScore}
        anomalies={diagnostics}
        recommendation={latestAnalysis?.recommendation || ''}
      />

      {/* Top Banner: Speakerphone Operation Guide */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40 p-4 sm:p-5 border border-slate-800">
        <div className="flex items-center space-x-3.5">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/30">
            <Radio className="h-6 w-6 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-sm sm:text-base font-bold text-white">
              Live Call Impersonation Interceptor (8-Vector Forensic Engine)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              🔊 <strong>Physical Setup:</strong> Place phone on speakerphone next to your PC. VoxSentinalX captures caller audio, filters user voice, and conducts 8-layer AI forensic checks.
            </p>
          </div>
        </div>

        {/* Start / Stop Stream Button */}
        <div className="mt-4 sm:mt-0 flex items-center space-x-3 w-full sm:w-auto">
          <button
            onClick={handleToggleMonitoring}
            className={`flex w-full sm:w-auto items-center justify-center space-x-2 rounded-xl px-5 py-3 text-sm font-bold text-white transition-all shadow-lg ${
              isMonitoring
                ? 'bg-red-600 hover:bg-red-500 shadow-red-600/30'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-cyan-500/30'
            }`}
          >
            {isMonitoring ? (
              <>
                <Square className="h-4 w-4 fill-current" />
                <span>Stop Monitoring</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-current" />
                <span>Start Live Monitoring</span>
              </>
            )}
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="rounded-xl bg-red-500/10 p-4 border border-red-500/30 text-red-300 text-xs">
          <strong>Error:</strong> {errorMessage}
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Telemetry, Radar, 8-Layer Decomposition (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Oscilloscope & Spectrogram Canvas */}
          <div className="rounded-2xl bg-slate-900/80 p-5 border border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Mic className={`h-4 w-4 ${isMonitoring ? 'text-cyan-400 animate-pulse' : 'text-slate-500'}`} />
                <span className="text-xs font-bold text-white uppercase tracking-wider">
                  Live Audio Telemetry & Oscilloscope
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-[11px] font-mono text-slate-400">
                  {latestAnalysis?.timestamp ? `Time: ${latestAnalysis.timestamp}` : 'Ready'}
                </span>
                <span className={`inline-flex h-2 w-2 rounded-full ${isMonitoring ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`} />
              </div>
            </div>

            {/* Canvas Visualizer */}
            <div className="relative overflow-hidden rounded-xl bg-slate-950 border border-slate-800/80 h-40">
              <canvas
                ref={canvasRef}
                width={640}
                height={160}
                className="w-full h-full block"
              />
              {!isMonitoring && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 text-center p-4">
                  <Mic className="h-7 w-7 text-slate-600 mb-1.5" />
                  <p className="text-xs font-medium text-slate-400">
                    Click "Start Live Monitoring" to begin real-time deepfake analysis.
                  </p>
                </div>
              )}
            </div>

            {/* Volume Input Meter */}
            <div className="mt-3 flex items-center space-x-3">
              <Volume2 className="h-4 w-4 text-slate-400 shrink-0" />
              <div className="flex-1 h-2 rounded-full bg-slate-950 overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-75"
                  style={{ width: `${Math.min(audioLevel * 300, 100)}%` }}
                />
              </div>
              <span className="text-[10px] font-mono text-slate-400 shrink-0">
                {Math.round(audioLevel * 100)}% Input
              </span>
            </div>
          </div>

          {/* 8-Layer Forensic Decomposition Breakdown */}
          <div className="rounded-2xl bg-slate-900/80 p-5 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  8-Vector Forensic Decomposition
                </h3>
              </div>
              <span className="text-[11px] text-slate-400 font-mono">Sliding Window: 2.0s</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              {/* Layer 1: Spectral */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L1: Spectral</span>
                <div className="mt-0.5 text-base font-mono font-bold text-white">
                  {Math.round(layerScores.spectral * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">Flatness & Phase</span>
              </div>

              {/* Layer 2: Prosody */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L2: Prosody</span>
                <div className="mt-0.5 text-base font-mono font-bold text-white">
                  {Math.round(layerScores.prosody * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">F0 Pitch Variance</span>
              </div>

              {/* Layer 3: Breathing */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L3: Breathing</span>
                <div className="mt-0.5 text-base font-mono font-bold text-white">
                  {Math.round(layerScores.breathing * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">Respiration Gaps</span>
              </div>

              {/* Layer 4: Vocoder */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L4: Vocoder</span>
                <div className="mt-0.5 text-base font-mono font-bold text-white">
                  {Math.round(layerScores.acoustic_artifacts * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">Filter Cutoff</span>
              </div>

              {/* Layer 5: LFCC */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L5: ASVspoof LFCC</span>
                <div className="mt-0.5 text-base font-mono font-bold text-cyan-400">
                  {Math.round(layerScores.lfcc * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">Linear Cepstrum ΔΔ</span>
              </div>

              {/* Layer 6: Glottal */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L6: Glottal Flow</span>
                <div className="mt-0.5 text-base font-mono font-bold text-cyan-400">
                  {Math.round(layerScores.glottal * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">LPC-NAQ Biomechanics</span>
              </div>

              {/* Layer 7: Perturbation */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L7: Perturbation</span>
                <div className="mt-0.5 text-base font-mono font-bold text-cyan-400">
                  {Math.round(layerScores.perturbation * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">Jitter & Shimmer</span>
              </div>

              {/* Layer 8: Bispectrum */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">L8: Bispectrum</span>
                <div className="mt-0.5 text-base font-mono font-bold text-cyan-400">
                  {Math.round(layerScores.bispectrum * 100)}%
                </div>
                <span className="text-[9px] text-slate-500 block truncate">QPC Phase Coupling</span>
              </div>
            </div>

            {/* Speaker Diarization Badge */}
            <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between rounded-xl bg-slate-950/50 p-3 border border-slate-800 text-xs">
              <div className="flex items-center space-x-2">
                <UserCheck className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300">
                  Channel Isolation: <strong>Caller ({Math.round(separation.caller_ratio * 100)}%)</strong> vs <strong>User ({Math.round(separation.user_ratio * 100)}%)</strong>
                </span>
              </div>
              <button
                onClick={onOpenCalibration}
                className="mt-2 sm:mt-0 text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 underline"
              >
                {separation.calibrated ? 'Recalibrate Profile' : 'Calibrate Voiceprint'}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Risk Gauge, Radar, Diagnostic Feed (5 Cols) */}
        <div className="lg:col-span-5 space-y-6 flex flex-col">
          {/* Risk Gauge */}
          <RiskGauge
            score={riskScore}
            level={riskLevel}
            isSpike={isSpike}
          />

          {/* Forensic Radar Chart */}
          <div className="rounded-2xl bg-slate-900/80 p-4 border border-slate-800 flex items-center justify-center">
            <ForensicRadar
              scores={layerScores}
              riskLevel={riskLevel}
            />
          </div>

          {/* Granular Diagnostic Messages Feed */}
          <div className="flex-1">
            <DiagnosticFeed
              anomalies={diagnostics}
              userMessage={latestAnalysis?.user_message}
              recommendation={latestAnalysis?.recommendation}
              suggestedActions={latestAnalysis?.suggested_actions}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
