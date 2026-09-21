import React, { useEffect, useRef, useState } from 'react';
import { Activity, Radio, ShieldCheck, Zap } from 'lucide-react';

interface WaveformHeroVisualizerProps {
  isSimulating?: boolean;
}

export const WaveformHeroVisualizer: React.FC<WaveformHeroVisualizerProps> = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [activeFrequency, setActiveFrequency] = useState<number>(440);
  const [simulatedScore, setSimulatedScore] = useState<number>(12);
  const [isInterceptActive, setIsInterceptActive] = useState<boolean>(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let phase = 0;
    const numBars = 64;

    const render = () => {
      // Handle canvas resolution
      const width = (canvas.width = canvas.offsetWidth * window.devicePixelRatio);
      const height = (canvas.height = canvas.offsetHeight * window.devicePixelRatio);

      ctx.clearRect(0, 0, width, height);

      // Draw subtle background grid within canvas
      ctx.strokeStyle = 'rgba(231, 226, 218, 0.6)'; // #E7E2DA border tone
      ctx.lineWidth = 1;
      const step = 32 * window.devicePixelRatio;
      for (let x = 0; x < width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // 1. Draw Multi-Band Frequency Bars
      const barWidth = width / (numBars * 1.5);
      const barSpacing = barWidth * 0.5;
      const startX = (width - (numBars * (barWidth + barSpacing))) / 2;

      for (let i = 0; i < numBars; i++) {
        const x = startX + i * (barWidth + barSpacing);
        // Harmonic noise simulation
        const dynamicHeight =
          Math.sin(phase + i * 0.2) * 0.35 +
          Math.sin(phase * 1.5 + i * 0.1) * 0.35 +
          Math.cos(phase * 0.8 + i * 0.05) * 0.3;

        const normalizedH = Math.max(0.08, (dynamicHeight + 1) / 2);
        const barH = normalizedH * (height * 0.45);
        const y = height / 2 - barH / 2;

        const grad = ctx.createLinearGradient(0, y, 0, y + barH);
        if (isInterceptActive) {
          grad.addColorStop(0, 'rgba(220, 38, 38, 0.85)'); // #DC2626
          grad.addColorStop(0.5, 'rgba(217, 119, 6, 0.7)'); // #D97706
          grad.addColorStop(1, 'rgba(220, 38, 38, 0.15)');
        } else {
          grad.addColorStop(0, 'rgba(194, 65, 12, 0.85)'); // #C2410C Saffron
          grad.addColorStop(0.5, 'rgba(21, 128, 61, 0.7)'); // #15803D Green
          grad.addColorStop(1, 'rgba(194, 65, 12, 0.12)');
        }

        ctx.fillStyle = grad;
        ctx.fillRect(x, y, barWidth, barH);
      }

      // 2. Draw Continuous Harmonic Sine Wave
      ctx.beginPath();
      ctx.lineWidth = 2.5 * window.devicePixelRatio;
      ctx.strokeStyle = isInterceptActive
        ? 'rgba(220, 38, 38, 0.9)' // #DC2626
        : 'rgba(194, 65, 12, 0.9)'; // #C2410C Active Audio Waveform
      ctx.shadowColor = isInterceptActive
        ? 'rgba(220, 38, 38, 0.35)'
        : 'rgba(194, 65, 12, 0.35)';
      ctx.shadowBlur = 8 * window.devicePixelRatio;

      for (let x = 0; x < width; x += 4) {
        const normX = x / width;
        const wave =
          Math.sin(normX * 12 + phase * 2) *
          Math.sin(normX * Math.PI) *
          (height * 0.25);
        const y = height / 2 + wave;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0; // reset shadow

      // 3. Draw Carrier Scan Line
      const scanX = ((phase * 80) % width);
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(194, 65, 12, 0.25)';
      ctx.lineWidth = 1.5;
      ctx.moveTo(scanX, height * 0.1);
      ctx.lineTo(scanX, height * 0.9);
      ctx.stroke();

      phase += 0.035;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    const interval = setInterval(() => {
      setActiveFrequency(Math.floor(220 + Math.random() * 3200));
      if (!isInterceptActive) {
        setSimulatedScore(Math.floor(8 + Math.random() * 12));
      }
    }, 1200);

    return () => {
      cancelAnimationFrame(animationFrameId);
      clearInterval(interval);
    };
  }, [isInterceptActive]);

  const toggleThreatMode = () => {
    setIsInterceptActive((prev) => {
      const next = !prev;
      setSimulatedScore(next ? 89 : 11);
      return next;
    });
  };

  return (
    <div className="relative w-full rounded-2xl overflow-hidden bg-white border border-[#E7E2DA] shadow-xs p-4 sm:p-6 transition-all duration-300">
      {/* HUD Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#ECE8E1] pb-3 mb-4">
        <div className="flex items-center space-x-2.5">
          <div className="relative flex h-3 w-3">
            <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${isInterceptActive ? 'bg-red-400' : 'bg-[#15803D]'}`}></span>
            <span className={`relative inline-flex h-3 w-3 rounded-full ${isInterceptActive ? 'bg-[#DC2626]' : 'bg-[#15803D]'}`}></span>
          </div>
          <span className="text-xs font-mono font-bold tracking-wider uppercase text-[#1E293B]">
            Acoustic Telemetry Scanner
          </span>
          <span className="hidden sm:inline-flex rounded bg-[#FFF1E8] px-2 py-0.5 text-[10px] font-mono text-[#C2410C] border border-[#E7E2DA] font-semibold">
            16 kHz Int16 PCM • 512-pt FFT
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5 text-[#64748B]">
            <Activity className="h-3.5 w-3.5 text-[#C2410C]" />
            <span>F0: <strong className="text-[#1E293B]">{activeFrequency} Hz</strong></span>
          </div>
          <button
            onClick={toggleThreatMode}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-all flex items-center space-x-1.5 ${
              isInterceptActive
                ? 'bg-red-50 text-[#DC2626] border-red-300 font-bold'
                : 'bg-[#F8F5EF] hover:bg-[#FFF1E8] text-[#1E293B] border-[#E7E2DA]'
            }`}
          >
            <Zap className="h-3 w-3" />
            <span>{isInterceptActive ? 'Inject Synthetic Threat' : 'Test Threat Pulse'}</span>
          </button>
        </div>
      </div>

      {/* Real-Time Canvas Waveform Area */}
      <div className="relative w-full h-44 sm:h-56 rounded-xl overflow-hidden bg-[#FDFBF7] border border-[#E7E2DA]">
        <canvas ref={canvasRef} className="w-full h-full block" />

        {/* Floating Scan Overlay Pills */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-2 pointer-events-none">
          <div className="bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-md text-[11px] font-mono flex items-center space-x-1.5 text-[#1E293B] border border-[#E7E2DA] shadow-xs">
            <Radio className="h-3 w-3 text-[#15803D] animate-pulse" />
            <span>Phase Coherence: <strong className="text-[#15803D]">98.4%</strong></span>
          </div>
          <div className="bg-white/90 backdrop-blur-md px-2.5 py-1 rounded-md text-[11px] font-mono flex items-center space-x-1.5 text-[#1E293B] border border-[#E7E2DA] shadow-xs">
            <ShieldCheck className="h-3 w-3 text-[#15803D]" />
            <span>NAQ Glottal Flow: <strong className="text-[#15803D]">0.141 (Natural)</strong></span>
          </div>
        </div>

        <div className="absolute bottom-3 right-3 pointer-events-none">
          <div className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-bold shadow-xs ${
            isInterceptActive
              ? 'bg-red-50 text-[#DC2626] border-red-300'
              : 'bg-emerald-50 text-[#15803D] border-emerald-300'
          }`}>
            Risk Score: {simulatedScore}% • {isInterceptActive ? '⚠️ SYNTHETIC DEEPFAKE' : '✅ AUTHENTIC HUMAN'}
          </div>
        </div>
      </div>
    </div>
  );
};
