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

      // Draw cyber background grid within canvas
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.04)';
      ctx.lineWidth = 1;
      const step = 30 * window.devicePixelRatio;
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
          grad.addColorStop(0, 'rgba(239, 68, 68, 0.85)');
          grad.addColorStop(0.5, 'rgba(245, 158, 11, 0.7)');
          grad.addColorStop(1, 'rgba(239, 68, 68, 0.2)');
        } else {
          grad.addColorStop(0, 'rgba(6, 182, 212, 0.9)');
          grad.addColorStop(0.5, 'rgba(16, 185, 129, 0.7)');
          grad.addColorStop(1, 'rgba(99, 102, 241, 0.2)');
        }

        ctx.fillStyle = grad;
        ctx.fillRect(x, y, barWidth, barH);
      }

      // 2. Draw Continuous Harmonic Sine Wave
      ctx.beginPath();
      ctx.lineWidth = 2.5 * window.devicePixelRatio;
      ctx.strokeStyle = isInterceptActive
        ? 'rgba(239, 68, 68, 0.85)'
        : 'rgba(6, 182, 212, 0.85)';
      ctx.shadowColor = isInterceptActive
        ? 'rgba(239, 68, 68, 0.6)'
        : 'rgba(6, 182, 212, 0.6)';
      ctx.shadowBlur = 12 * window.devicePixelRatio;

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
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
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
    <div className="relative w-full rounded-2xl overflow-hidden glass-panel border border-cyan-500/20 shadow-neon-cyan p-4 sm:p-6 transition-all duration-300">
      {/* HUD Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center space-x-2.5">
          <div className="relative flex h-3 w-3">
            <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${isInterceptActive ? 'bg-red-400' : 'bg-cyan-400'}`}></span>
            <span className={`relative inline-flex h-3 w-3 rounded-full ${isInterceptActive ? 'bg-red-500' : 'bg-cyan-500'}`}></span>
          </div>
          <span className="text-xs font-mono font-bold tracking-wider uppercase text-slate-300">
            Acoustic Telemetry Scanner
          </span>
          <span className="hidden sm:inline-flex rounded bg-cyan-950/80 px-2 py-0.5 text-[10px] font-mono text-cyan-400 border border-cyan-800/60">
            16 kHz Int16 PCM • 512-pt FFT
          </span>
        </div>

        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="flex items-center space-x-1.5 text-slate-400">
            <Activity className="h-3.5 w-3.5 text-cyan-400" />
            <span>F0: <strong className="text-cyan-300">{activeFrequency} Hz</strong></span>
          </div>
          <button
            onClick={toggleThreatMode}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium border transition-all flex items-center space-x-1.5 ${
              isInterceptActive
                ? 'bg-red-500/20 text-red-300 border-red-500/40 glow-red'
                : 'bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 border-slate-700'
            }`}
          >
            <Zap className="h-3 w-3" />
            <span>{isInterceptActive ? 'Inject Synthetic Threat' : 'Test Threat Pulse'}</span>
          </button>
        </div>
      </div>

      {/* Real-Time Canvas Waveform Area */}
      <div className="relative w-full h-44 sm:h-56 rounded-xl overflow-hidden bg-slate-950/80 border border-slate-800/80">
        <canvas ref={canvasRef} className="w-full h-full block" />

        {/* Floating Scan Overlay Pills */}
        <div className="absolute top-3 left-3 flex flex-wrap gap-2 pointer-events-none">
          <div className="glass-card px-2.5 py-1 rounded-md text-[11px] font-mono flex items-center space-x-1.5 text-slate-300">
            <Radio className="h-3 w-3 text-cyan-400 animate-pulse" />
            <span>Phase Coherence: <strong className="text-emerald-400">98.4%</strong></span>
          </div>
          <div className="glass-card px-2.5 py-1 rounded-md text-[11px] font-mono flex items-center space-x-1.5 text-slate-300">
            <ShieldCheck className="h-3 w-3 text-emerald-400" />
            <span>NAQ Glottal Flow: <strong className="text-emerald-400">0.141 (Natural)</strong></span>
          </div>
        </div>

        <div className="absolute bottom-3 right-3 pointer-events-none">
          <div className={`px-3 py-1.5 rounded-lg border text-xs font-mono font-bold shadow-lg ${
            isInterceptActive
              ? 'bg-red-950/90 text-red-400 border-red-500/50 glow-red'
              : 'bg-cyan-950/90 text-cyan-300 border-cyan-500/40 glow-cyan'
          }`}>
            Risk Score: {simulatedScore}% • {isInterceptActive ? '⚠️ SYNTHETIC DEEPFAKE' : '✅ AUTHENTIC HUMAN'}
          </div>
        </div>
      </div>
    </div>
  );
};
