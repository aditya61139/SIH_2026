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

      // Draw subtle background grid within canvas (Divider: #252830)
      ctx.strokeStyle = 'rgba(37, 40, 48, 0.8)';
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
          grad.addColorStop(0, 'rgba(239, 68, 68, 0.85)'); // #EF4444
          grad.addColorStop(0.5, 'rgba(245, 158, 11, 0.7)'); // #F59E0B
          grad.addColorStop(1, 'rgba(239, 68, 68, 0.15)');
        } else {
          grad.addColorStop(0, 'rgba(16, 185, 129, 0.85)'); // #10B981 Emerald
          grad.addColorStop(0.5, 'rgba(5, 150, 105, 0.7)');
          grad.addColorStop(1, 'rgba(16, 185, 129, 0.12)');
        }

        ctx.fillStyle = grad;
        ctx.fillRect(x, y, barWidth, barH);
      }

      // 2. Draw Continuous Harmonic Sine Wave (Active: #10B981)
      ctx.beginPath();
      ctx.lineWidth = 2.5 * window.devicePixelRatio;
      ctx.strokeStyle = isInterceptActive
        ? 'rgba(239, 68, 68, 0.95)' // #EF4444
        : 'rgba(16, 185, 129, 0.95)'; // #10B981 Active Audio Waveform
      ctx.shadowColor = isInterceptActive
        ? 'rgba(239, 68, 68, 0.45)'
        : 'rgba(16, 185, 129, 0.45)';
      ctx.shadowBlur = 10 * window.devicePixelRatio;

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
      ctx.strokeStyle = 'rgba(16, 185, 129, 0.3)';
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
    <div className="relative w-full rounded-2xl overflow-hidden bg-[#1A1C23] border border-[#2A2E37] shadow-xl p-4 sm:p-6 transition-all duration-300">
      {/* HUD Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#252830] pb-3 mb-4">
        <div className="flex items-center space-x-2.5">
          <div className="relative flex h-3 w-3">
            <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${isInterceptActive ? 'bg-red-400' : 'bg-[#10B981]'}`}></span>
            <span className={`relative inline-flex h-3 w-3 rounded-full ${isInterceptActive ? 'bg-[#EF4444]' : 'bg-[#10B981]'}`}></span>
          </div>
          <span className="text-xs font-mono font-bold tracking-wider uppercase text-white">
            Acoustic Telemetry Scanner
          </span>
          <span className="hidden sm:inline-flex rounded bg-[#10B981]/10 px-2 py-0.5 text-[10px] font-mono text-[#10B981] border border-[#10B981]/30 font-semibold">
            16 kHz Int16 PCM • 512-pt FFT
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5 text-[#94A3B8]">
            <Activity className="h-3.5 w-3.5 text-[#10B981]" />
            <span>F0: <strong className="text-white">{activeFrequency} Hz</strong></span>
          </div>
          <button
            onClick={toggleThreatMode}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-all flex items-center space-x-1.5 ${
              isInterceptActive
                ? 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/40 font-bold'
                : 'bg-[#15171C] hover:bg-[#10B981]/10 text-[#E2E8F0] hover:text-[#10B981] border-[#2A2E37]'
            }`}
          >
            <Zap className="h-3 w-3" />
            <span>{isInterceptActive ? 'Inject Synthetic Threat' : 'Test Threat Pulse'}</span>
          </button>
        </div>
      </div>

      {/* Real-Time Canvas Waveform Area */}
      <div className="relative w-full h-44 sm:h-56 rounded-xl overflow-hidden bg-[#15171C] border border-[#2A2E37]">
        <canvas ref={canvasRef} className="w-full h-full block" />

        {/* Floating Scan Overlay Pills */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-2 pointer-events-none">
          <div className="bg-[#1A1C23]/90 backdrop-blur-md px-2.5 py-1 rounded-md text-[11px] font-mono flex items-center space-x-1.5 text-[#E2E8F0] border border-[#2A2E37] shadow-xs">
            <Radio className="h-3 w-3 text-[#10B981] animate-pulse" />
            <span>Phase Coherence: <strong className="text-[#10B981]">98.4%</strong></span>
          </div>
          <div className="bg-[#1A1C23]/90 backdrop-blur-md px-2.5 py-1 rounded-md text-[11px] font-mono flex items-center space-x-1.5 text-[#E2E8F0] border border-[#2A2E37] shadow-xs">
            <ShieldCheck className="h-3 w-3 text-[#10B981]" />
            <span>NAQ Glottal Flow: <strong className="text-[#10B981]">0.141 (Natural)</strong></span>
          </div>
        </div>

        <div className="absolute bottom-3 right-3 pointer-events-none">
          <div className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-bold shadow-xs ${
            isInterceptActive
              ? 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30'
              : 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/30'
          }`}>
            Risk Score: {simulatedScore}% • {isInterceptActive ? '⚠️ SYNTHETIC DEEPFAKE' : '✅ AUTHENTIC HUMAN'}
          </div>
        </div>
      </div>
    </div>
  );
};
