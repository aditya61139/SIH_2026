import React, { useState, useEffect, useRef } from 'react';
import { Play, Square, Mic, Volume2, ShieldCheck, UserCheck, Layers, Radio, RotateCcw } from 'lucide-react';
import { VoxSentinalAudioCapture } from '../lib/audioCapture';
import { CanvasAudioVisualizer } from '../lib/audioVisualizer';
import { RiskGauge } from './RiskGauge';
import { DiagnosticFeed } from './DiagnosticFeed';
import { AlertOverlay } from './AlertOverlay';
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
  const alertAcknowledgedRef = useRef<boolean>(false);

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

          // Trigger Alert modal on CRITICAL risk only if not already dismissed for this incident
          if (data.risk_level === 'CRITICAL') {
            if (!alertAcknowledgedRef.current) {
              setShowAlertModal(true);
            }
          } else if (data.risk_level === 'LOW' || data.risk_level === 'MODERATE') {
            // Re-arm alert when threat level subsides
            alertAcknowledgedRef.current = false;
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

  const handleResetTelemetry = () => {
    captureEngine.resetSession();
    setLatestAnalysis(null);
    setShowAlertModal(false);
    alertAcknowledgedRef.current = false;
    visualizerRef.current?.setRiskLevel('LOW');
  };

  const handleCloseAlertModal = () => {
    setShowAlertModal(false);
    alertAcknowledgedRef.current = true; // Dismiss for current active threat incident
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
  const layerScores = latestAnalysis?.layer_scores ?? {};
  const separation = latestAnalysis?.speaker_separation ?? {
    caller_ratio: 1.0,
    user_ratio: 0.0,
    calibrated: false,
  };
  const shap = latestAnalysis?.domain_shap_contributions ?? {};

  return (
    <div className="space-y-6">
      {/* Alert Overlay Popup */}
      <AlertOverlay
        isOpen={showAlertModal}
        onClose={handleCloseAlertModal}
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
            <h2 className="text-sm sm:text-base font-bold text-white flex items-center space-x-2">
              <span>Live Call Impersonation Interceptor</span>
              <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800">
                Multi-Domain AI Engine v2.0
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              🔊 <strong>Physical Setup:</strong> Place phone on speakerphone next to laptop. VoxSentinalX runs 6-domain forensic checks (Compression Δk, Jitter/Shimmer, Phase Coherence, Acoustic Dynamics).
            </p>
          </div>
        </div>

        {/* Start / Stop & Reset Buttons */}
        <div className="mt-4 sm:mt-0 flex items-center space-x-2.5 w-full sm:w-auto">
          <button
            onClick={handleResetTelemetry}
            title="Reset telemetry, baseline, and alert counters"
            className="flex items-center justify-center space-x-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 px-3.5 py-3 text-xs font-semibold text-slate-300 border border-slate-700 transition-all"
          >
            <RotateCcw className="h-4 w-4 text-cyan-400" />
            <span>Reset Telemetry</span>
          </button>

          <button
            onClick={handleToggleMonitoring}
            className={`flex flex-1 sm:flex-initial items-center justify-center space-x-2 rounded-xl px-5 py-3 text-sm font-bold text-white transition-all shadow-lg ${
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

      {/* Main Grid: Visualizer & Risk Gauge + Diagnostics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Visualizer, Meter, 6-Domain Breakdown (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Real-time Oscilloscope & Spectrogram Canvas */}
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
            <div className="relative overflow-hidden rounded-xl bg-slate-950 border border-slate-800/80 h-44">
              <canvas
                ref={canvasRef}
                width={640}
                height={176}
                className="w-full h-full block"
              />
              {!isMonitoring && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 text-center p-4">
                  <Mic className="h-8 w-8 text-slate-600 mb-2" />
                  <p className="text-xs font-medium text-slate-400">
                    Click "Start Live Monitoring" to begin capturing live call stream.
                  </p>
                </div>
              )}
            </div>

            {/* Input Volume Bar */}
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

          {/* 6-Domain Forensic Scores Breakdown (ITEGAM-JETIA 2026 Framework) */}
          <div className="rounded-2xl bg-slate-900/80 p-5 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  6-Domain Multi-Feature Forensic Framework
                </h3>
              </div>
              <span className="text-[11px] text-cyan-400 font-mono">Chhatriwala et al. 2026</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {/* Domain 1: Compression */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-cyan-400 uppercase font-bold block">
                    D1: Compression
                  </span>
                  <span className="text-[9px] font-mono text-slate-400">#1 SHAP</span>
                </div>
                <div className="mt-1 text-lg font-mono font-bold text-white">
                  {Math.round((layerScores.compression ?? 0) * 100)}%
                </div>
                <span className="text-[9px] text-slate-400 block truncate">
                  Mel-Band Δk Distortion
                </span>
              </div>

              {/* Domain 2: Acoustic */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  D2: Acoustic
                </span>
                <div className="mt-1 text-lg font-mono font-bold text-white">
                  {Math.round((layerScores.acoustic ?? 0) * 100)}%
                </div>
                <span className="text-[9px] text-slate-400 block truncate">
                  MFCC + Δ + Δ² (39-dim)
                </span>
              </div>

              {/* Domain 3: Prosody */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  D3: Prosody
                </span>
                <div className="mt-1 text-lg font-mono font-bold text-white">
                  {Math.round((layerScores.prosody ?? 0) * 100)}%
                </div>
                <span className="text-[9px] text-slate-400 block truncate">
                  Jitter, Shimmer, F0
                </span>
              </div>

              {/* Domain 4: Phase */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  D4: Phase Delay
                </span>
                <div className="mt-1 text-lg font-mono font-bold text-white">
                  {Math.round((layerScores.phase ?? 0) * 100)}%
                </div>
                <span className="text-[9px] text-slate-400 block truncate">
                  Group Delay τg / Inst Freq
                </span>
              </div>

              {/* Domain 5: Spectral Entropy */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  D5: Spectral
                </span>
                <div className="mt-1 text-lg font-mono font-bold text-white">
                  {Math.round((layerScores.spectral ?? 0) * 100)}%
                </div>
                <span className="text-[9px] text-slate-400 block truncate">
                  Entropy Hs / Flatness SF
                </span>
              </div>

              {/* Domain 6: Respiration / Artifacts */}
              <div className="rounded-xl bg-slate-950/70 p-3 border border-slate-800/80">
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  D6: Respiration
                </span>
                <div className="mt-1 text-lg font-mono font-bold text-white">
                  {Math.round((layerScores.breathing ?? 0) * 100)}%
                </div>
                <span className="text-[9px] text-slate-400 block truncate">
                  Breath Pause Intervals
                </span>
              </div>
            </div>

            {/* Speaker Diarization Badge */}
            <div className="mt-4 flex flex-col sm:flex-row sm:items-center justify-between rounded-xl bg-slate-950/50 p-3 border border-slate-800 text-xs">
              <div className="flex items-center space-x-2">
                <UserCheck className="h-4 w-4 text-emerald-400" />
                <span className="text-slate-300">
                  Channel Isolation: <strong>Caller Voice ({Math.round(separation.caller_ratio * 100)}%)</strong> vs <strong>Local User ({Math.round(separation.user_ratio * 100)}%)</strong>
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

        {/* Right Column: Risk Gauge & Granular Diagnostic Feed (5 Cols) */}
        <div className="lg:col-span-5 space-y-6 flex flex-col">
          {/* Dynamic Risk Gauge */}
          <RiskGauge
            score={riskScore}
            level={riskLevel}
            isSpike={isSpike}
          />

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
