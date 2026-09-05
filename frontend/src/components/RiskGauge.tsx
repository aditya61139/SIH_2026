import React from 'react';
import { RiskLevel } from '../types';
import { ShieldAlert, ShieldCheck, AlertTriangle, Flame } from 'lucide-react';

interface RiskGaugeProps {
  score: number; // 0.0 to 1.0
  level: RiskLevel;
  isSpike?: boolean;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ score, level, isSpike = false }) => {
  const percentage = Math.round(score * 100);

  // Determine Colors & Config based on risk
  let color = '#10b981'; // Green
  let glowClass = 'glow-green';
  let badgeText = 'GENUINE HUMAN';
  let badgeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  let Icon = ShieldCheck;

  if (level === 'CRITICAL') {
    color = '#ef4444';
    glowClass = 'glow-red';
    badgeText = 'CRITICAL AI CLONE';
    badgeBg = 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse';
    Icon = Flame;
  } else if (level === 'HIGH') {
    color = '#f97316';
    glowClass = 'glow-amber';
    badgeText = 'SUSPICIOUS / FAKE';
    badgeBg = 'bg-orange-500/10 text-orange-400 border-orange-500/30';
    Icon = ShieldAlert;
  } else if (level === 'MODERATE') {
    color = '#f59e0b';
    glowClass = 'glow-amber';
    badgeText = 'CAUTION';
    badgeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    Icon = AlertTriangle;
  }

  // SVG Gauge Calculations
  const radius = 75;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score * circumference * 0.75); // 270 degree arc

  return (
    <div className={`relative flex flex-col items-center justify-center rounded-2xl bg-slate-900/80 p-6 border border-slate-800 transition-all ${glowClass}`}>
      {isSpike && (
        <div className="absolute top-3 right-3 flex items-center space-x-1 rounded-full bg-red-500/20 px-2 py-0.5 text-[11px] font-bold text-red-400 border border-red-500/40 animate-bounce">
          <span>⚡ VOICE SWAP SPIKE</span>
        </div>
      )}

      {/* SVG Circular Meter */}
      <div className="relative flex items-center justify-center">
        <svg className="h-48 w-48 transform -rotate-[135deg]" viewBox="0 0 180 180">
          {/* Background Track */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke="#1e293b"
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * 0.25}
            strokeLinecap="round"
          />
          {/* Active Colored Arc */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
          />
        </svg>

        {/* Central Display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <Icon className="h-6 w-6 mb-1 transition-colors" style={{ color }} />
          <div className="text-4xl font-extrabold tracking-tight text-white font-mono">
            {percentage}<span className="text-2xl font-normal text-slate-400">%</span>
          </div>
          <span className="text-[11px] uppercase tracking-wider text-slate-400 mt-0.5">
            Risk Score
          </span>
        </div>
      </div>

      {/* Badge Pill */}
      <div className={`mt-2 flex items-center space-x-1.5 rounded-full px-3 py-1 text-xs font-bold border ${badgeBg}`}>
        <span>{badgeText}</span>
      </div>

      {/* Threshold Legend Bar */}
      <div className="mt-4 flex w-full justify-between text-[10px] text-slate-400 px-2">
        <span className="text-emerald-400">0% Genuine</span>
        <span className="text-amber-400">30% Caution</span>
        <span className="text-orange-400">60% Warning</span>
        <span className="text-red-400">80% Critical</span>
      </div>
    </div>
  );
};
