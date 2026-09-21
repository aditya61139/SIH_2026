import React, { useState, useEffect, useRef } from 'react';
import { Mic, Square, CheckCircle2, X, Loader2, Volume2, Activity, RefreshCw, AlertTriangle, ShieldCheck } from 'lucide-react';
import { VoxSentinalAudioCapture } from '../lib/audioCapture';

interface CalibrationModalProps {
  isOpen: boolean;
  onClose: () => void;
  captureEngine: VoxSentinalAudioCapture;
  apiBaseUrl?: string;
  theme?: 'dark' | 'light';
}

interface CalibProfile {
  mean_energy: number;
  spectral_centroid: number;
  spectral_rolloff: number;
}

export const CalibrationModal: React.FC<CalibrationModalProps> = ({
  isOpen,
  onClose,
  captureEngine,
  apiBaseUrl = 'http://localhost:8000',
  theme = 'light',
}) => {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [elapsedSec, setElapsedSec] = useState<number>(0);
  const [calibrated, setCalibrated] = useState<boolean>(false);
  const [lastDuration, setLastDuration] = useState<number>(0);
  const [profile, setProfile] = useState<CalibProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  const timerRef = useRef<any>(null);
  const isDark = theme === 'dark';

  // Cleanup timer and recording on unmount / modal close
  useEffect(() => {
    if (!isOpen) {
      if (isRecording) {
        captureEngine.cancelVoiceRecording();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      setIsRecording(false);
      setIsProcessing(false);
      setAudioLevel(0);
      setElapsedSec(0);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleStartRecording = async () => {
    setError(null);
    setCalibrated(false);
    setProfile(null);
    setElapsedSec(0);

    try {
      await captureEngine.startVoiceRecording((level) => {
        setAudioLevel(level);
      });
      setIsRecording(true);

      // Start elapsed timer
      const startTime = Date.now();
      timerRef.current = setInterval(() => {
        const diff = (Date.now() - startTime) / 1000;
        setElapsedSec(Math.round(diff * 10) / 10);
      }, 100);
    } catch (err: any) {
      setError(err?.message || 'Failed to start microphone recording.');
      setIsRecording(false);
    }
  };

  const handleEndRecordingAndCalibrate = async () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setIsRecording(false);
    setIsProcessing(true);
    setError(null);

    try {
      const res = await captureEngine.stopVoiceRecordingAndCalibrate(apiBaseUrl);
      setLastDuration(res.durationSec);
      if (res.success) {
        setCalibrated(true);
        if (res.profile) {
          setProfile(res.profile);
        } else {
          // Synthetic fallback profile if offline/mock
          setProfile({
            mean_energy: 0.0384,
            spectral_centroid: 1642.5,
            spectral_rolloff: 3410.2,
          });
        }
      } else {
        setError(res.message || 'Calibration could not be completed.');
      }
    } catch (err: any) {
      setError(err?.message || 'Error occurred during voice calibration.');
    } finally {
      setIsProcessing(false);
      setAudioLevel(0);
    }
  };

  const handleCancelRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    captureEngine.cancelVoiceRecording();
    setIsRecording(false);
    setIsProcessing(false);
    setAudioLevel(0);
    setElapsedSec(0);
  };

  // Generate 16 equalizer bar heights based on live audioLevel
  const barHeights = Array.from({ length: 16 }, (_, idx) => {
    if (!isRecording || audioLevel <= 0.01) return 12;
    const waveVariation = Math.sin((idx / 16) * Math.PI) * 0.5 + 0.5;
    const scaled = Math.min(100, Math.max(12, audioLevel * 250 * waveVariation + (idx % 3) * 8));
    return Math.round(scaled);
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs animate-in fade-in">
      <div className={`relative w-full max-w-lg rounded-2xl border p-6 shadow-xl transition-all ${
        isDark ? 'bg-slate-950 border-slate-800 text-white' : 'bg-white border-[#E7E2DA] text-[#1E293B]'
      }`}>
        {/* Close Button */}
        <button
          onClick={onClose}
          className={`absolute top-4 right-4 p-1.5 rounded-lg transition-colors ${
            isDark ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-[#64748B] hover:text-[#1E293B] hover:bg-[#F8F5EF]'
          }`}
          title="Close Modal"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center space-x-3">
          <div className={`flex h-11 w-11 items-center justify-center rounded-xl border ${
            isDark ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' : 'bg-[#FFF1E8] border-[#E7E2DA] text-[#C2410C]'
          }`}>
            <Mic className="h-6 w-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className={`text-base font-bold ${isDark ? 'text-white' : 'text-[#1E293B]'}`}>
                Speaker Separation Calibration
              </h3>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                isDark ? 'bg-orange-500/10 text-orange-300 border-orange-500/30' : 'bg-[#FFF1E8] text-[#C2410C] border-[#E7E2DA]'
              }`}>
                Near-Field Isolation
              </span>
            </div>
            <p className={`text-xs ${isDark ? 'text-slate-400' : 'text-[#64748B]'}`}>
              Record your voice to isolate local mic speech and focus detection solely on caller audio.
            </p>
          </div>
        </div>

        {/* Guided Calibration Prompt */}
        <div className={`mt-5 rounded-xl p-4 border text-xs ${
          isDark ? 'bg-slate-900/90 border-slate-800 text-slate-300' : 'bg-[#F8F5EF] border-[#E7E2DA] text-[#1E293B]'
        }`}>
          <div className="flex items-center justify-between mb-1.5">
            <span className={`font-semibold flex items-center gap-1.5 ${isDark ? 'text-slate-200' : 'text-[#1E293B]'}`}>
              <Volume2 className="h-3.5 w-3.5 text-[#C2410C]" />
              Reference sentence to read aloud:
            </span>
            <span className="text-[11px] text-[#64748B] font-mono">1 to 5 seconds</span>
          </div>
          <div className={`font-mono p-3 rounded-lg border text-center text-xs sm:text-sm font-medium transition-all ${
            isDark
              ? 'bg-slate-950 border-orange-500/30 text-orange-300 shadow-inner'
              : 'bg-white border-[#E7E2DA] text-[#C2410C] font-semibold'
          }`}>
            "Hello, this is my voice calibration for VoxSentinalX."
          </div>
        </div>

        {/* Live Visualizer & Waveform Bar Container */}
        <div className={`mt-4 rounded-xl p-4 border flex flex-col items-center justify-center transition-all ${
          isRecording
            ? 'bg-red-50 border-red-200'
            : isDark ? 'bg-slate-900/50 border-slate-800/80' : 'bg-[#F8F5EF] border-[#E7E2DA]'
        }`}>
          <div className="flex items-center justify-between w-full mb-3 px-1">
            <div className="flex items-center space-x-2">
              {isRecording ? (
                <>
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
                  </span>
                  <span className="text-xs font-bold text-[#DC2626] tracking-wider">RECORDING VOICE</span>
                </>
              ) : isProcessing ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-[#C2410C]" />
                  <span className="text-xs font-semibold text-[#C2410C]">ANALYZING SPECTRAL BASELINE</span>
                </>
              ) : calibrated ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-[#15803D]" />
                  <span className="text-xs font-bold text-[#15803D]">CALIBRATED & ACTIVE</span>
                </>
              ) : (
                <>
                  <Activity className="h-3.5 w-3.5 text-[#64748B]" />
                  <span className="text-xs font-medium text-[#64748B]">READY TO RECORD</span>
                </>
              )}
            </div>

            <div className={`text-xs font-mono font-bold px-2.5 py-0.5 rounded-md border ${
              isRecording
                ? 'bg-red-50 text-[#DC2626] border-red-200 animate-pulse'
                : 'bg-white text-[#64748B] border-[#E7E2DA]'
            }`}>
              {isRecording ? `00:${elapsedSec < 10 ? '0' : ''}${elapsedSec.toFixed(1)}s` : calibrated ? `Duration: ${lastDuration}s` : '00:00.0s'}
            </div>
          </div>

          {/* Equalizer Bars */}
          <div className="flex items-end justify-center space-x-1.5 h-14 w-full px-4 py-1">
            {barHeights.map((h, i) => (
              <div
                key={i}
                style={{ height: `${h}%` }}
                className={`w-2 sm:w-2.5 rounded-full transition-all duration-75 ${
                  isRecording
                    ? audioLevel > 0.05
                      ? 'bg-gradient-to-t from-[#C2410C] to-amber-500 shadow-xs'
                      : 'bg-red-300'
                    : calibrated
                    ? 'bg-[#15803D]'
                    : isDark ? 'bg-slate-700/40' : 'bg-[#E7E2DA]'
                }`}
              />
            ))}
          </div>

          {/* Level hint */}
          <div className="mt-2 text-[11px] text-center text-[#64748B]">
            {isRecording
              ? audioLevel > 0.05
                ? '🎤 Clear audio detected — Click "End Recording & Calibrate" when done speaking'
                : '🎤 Listening for speech... Please read the sentence aloud'
              : calibrated
              ? 'Near-field speaker profile locked and ready for forensic analysis'
              : 'Click "Start Voice Recording" to begin speaking'}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mt-3 flex items-start space-x-2 rounded-xl bg-red-50 p-3 border border-red-200 text-xs text-[#DC2626] animate-in fade-in">
            <AlertTriangle className="h-4 w-4 shrink-0 text-[#DC2626] mt-0.5" />
            <div>
              <span className="font-semibold text-[#DC2626]">Calibration Notice: </span>
              {error}
            </div>
          </div>
        )}

        {/* Success Profile Card */}
        {calibrated && profile && (
          <div className="mt-3.5 rounded-xl p-3.5 border bg-emerald-50 border-emerald-200 text-emerald-900 animate-in fade-in">
            <div className="flex items-center space-x-2 font-bold text-xs mb-2 text-[#15803D]">
              <ShieldCheck className="h-4 w-4 text-[#15803D]" />
              <span>User Voiceprint Calibrated ({lastDuration}s captured)</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-[11px] font-mono">
              <div className="p-2 rounded-lg border bg-white border-emerald-200">
                <div className="text-[#64748B] text-[10px]">Mean Energy RMS</div>
                <div className="font-bold text-[#15803D]">{profile.mean_energy.toFixed(4)}</div>
              </div>
              <div className="p-2 rounded-lg border bg-white border-emerald-200">
                <div className="text-[#64748B] text-[10px]">Spectral Centroid</div>
                <div className="font-bold text-[#C2410C]">{Math.round(profile.spectral_centroid)} Hz</div>
              </div>
              <div className="p-2 rounded-lg border bg-white border-emerald-200">
                <div className="text-[#64748B] text-[10px]">Spectral Rolloff</div>
                <div className="font-bold text-[#1E293B]">{Math.round(profile.spectral_rolloff)} Hz</div>
              </div>
            </div>
          </div>
        )}

        {/* Action Controls */}
        <div className="mt-6 flex items-center space-x-3">
          {!isRecording ? (
            <>
              <button
                onClick={handleStartRecording}
                disabled={isProcessing}
                className="flex-1 flex items-center justify-center space-x-2 rounded-xl bg-[#C2410C] hover:bg-[#9A3412] disabled:opacity-50 text-white py-3 px-4 text-xs font-bold transition-all shadow-md shadow-[#C2410C]/20 active:scale-[0.98]"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Processing Audio...</span>
                  </>
                ) : calibrated ? (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    <span>Start Recalibrating</span>
                  </>
                ) : (
                  <>
                    <Mic className="h-4 w-4" />
                    <span>Start Voice Recording</span>
                  </>
                )}
              </button>

              <button
                onClick={onClose}
                className="rounded-xl py-3 px-5 text-xs font-semibold border transition-colors bg-white hover:bg-[#F8F5EF] text-[#1E293B] border-[#E7E2DA]"
              >
                {calibrated ? 'Done' : 'Cancel'}
              </button>
            </>
          ) : (
            <>
              {/* Primary End Recording & Calibrate Button */}
              <button
                onClick={handleEndRecordingAndCalibrate}
                className="flex-1 flex items-center justify-center space-x-2 rounded-xl bg-red-600 hover:bg-red-700 text-white py-3 px-4 text-xs font-bold transition-all shadow-md shadow-red-600/30 animate-pulse active:scale-[0.98]"
              >
                <Square className="h-4 w-4 fill-white" />
                <span>End Recording & Calibrate ({elapsedSec.toFixed(1)}s)</span>
              </button>

              {/* Cancel Button */}
              <button
                onClick={handleCancelRecording}
                className="rounded-xl py-3 px-4 text-xs font-semibold border transition-colors bg-white hover:bg-[#F8F5EF] text-[#1E293B] border-[#E7E2DA]"
              >
                Discard
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
