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

  // Cyber Dark Theme Risk Colors
  let color = '#10B981'; // Low Risk / Safe (#10B981)
  let badgeText = 'AUTHENTIC VOICE';
  let badgeBg = 'bg-[#10B981]/15 text-[#10B981] border-[#10B981]/30';
  let Icon = ShieldCheck;

  if (level === 'CRITICAL') {
    color = '#DC2626'; // Critical Error (#DC2626)
    badgeText = 'CRITICAL AI CLONE';
    badgeBg = 'bg-[#DC2626]/20 text-[#DC2626] border-[#DC2626]/40 animate-pulse font-bold';
    Icon = Flame;
  } else if (level === 'HIGH') {
    color = '#EF4444'; // High Risk / Clone Detected (#EF4444)
    badgeText = 'HIGH RISK / CLONE';
    badgeBg = 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30 font-bold';
    Icon = ShieldAlert;
  } else if (level === 'MODERATE') {
    color = '#F59E0B'; // Medium Risk / Suspicious (#F59E0B)
    badgeText = 'SUSPICIOUS SPEECH';
    badgeBg = 'bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30 font-bold';
    Icon = AlertTriangle;
  }

  // SVG Gauge Calculations
  const radius = 75;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score * circumference * 0.75); // 270 degree arc

  return (
    <div className="relative flex flex-col items-center justify-center rounded-2xl bg-[#1A1C23] p-6 border border-[#2A2E37] shadow-xl transition-all">
      {isSpike && (
        <div className="absolute top-3 right-3 flex items-center space-x-1 rounded-full bg-[#EF4444]/20 px-2 py-0.5 text-[11px] font-bold text-[#EF4444] border border-[#EF4444]/40 animate-bounce">
          <span>⚡ VOICE SWAP SPIKE</span>
        </div>
      )}

      {/* SVG Circular Meter */}
      <div className="relative flex items-center justify-center">
        <svg className="h-48 w-48 transform -rotate-[135deg]" viewBox="0 0 180 180">
          {/* Background Track (Audio Track: #374151) */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke="#374151"
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
            {percentage}<span className="text-2xl font-normal text-[#94A3B8]">%</span>
          </div>
          <span className="text-[11px] uppercase tracking-wider text-[#94A3B8] mt-0.5 font-medium">
            Risk Score
          </span>
        </div>
      </div>

      {/* Badge Pill */}
      <div className={`mt-2 flex items-center space-x-1.5 rounded-full px-3 py-1 text-xs font-bold border ${badgeBg}`}>
        <span>{badgeText}</span>
      </div>

      {/* Threshold Legend Bar */}
      <div className="mt-4 flex w-full justify-between text-[10px] text-[#64748B] px-2 font-mono">
        <span className="text-[#10B981] font-semibold">0% Genuine</span>
        <span className="text-[#F59E0B] font-semibold">30% Caution</span>
        <span className="text-[#EF4444] font-semibold">60% Warning</span>
        <span className="text-[#DC2626] font-semibold">80% Critical</span>
      </div>
    </div>
  );
};
