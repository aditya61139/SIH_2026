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

  // Swadesi Colors & Config based on risk
  let color = '#15803D'; // Safe / Low Risk (#15803D)
  let badgeText = 'GENUINE HUMAN';
  let badgeBg = 'bg-emerald-50 text-[#15803D] border-emerald-200';
  let Icon = ShieldCheck;

  if (level === 'CRITICAL') {
    color = '#DC2626'; // Critical / High Risk
    badgeText = 'CRITICAL AI CLONE';
    badgeBg = 'bg-red-50 text-[#DC2626] border-red-200 animate-pulse font-bold';
    Icon = Flame;
  } else if (level === 'HIGH') {
    color = '#DC2626'; // High Risk
    badgeText = 'HIGH RISK / FAKE';
    badgeBg = 'bg-red-50 text-[#DC2626] border-red-200 font-bold';
    Icon = ShieldAlert;
  } else if (level === 'MODERATE') {
    color = '#D97706'; // Medium / Suspicious
    badgeText = 'SUSPICIOUS / CAUTION';
    badgeBg = 'bg-amber-50 text-[#D97706] border-amber-200 font-bold';
    Icon = AlertTriangle;
  }

  // SVG Gauge Calculations
  const radius = 75;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score * circumference * 0.75); // 270 degree arc

  return (
    <div className="relative flex flex-col items-center justify-center rounded-2xl bg-white p-6 border border-[#E7E2DA] shadow-xs transition-all">
      {isSpike && (
        <div className="absolute top-3 right-3 flex items-center space-x-1 rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-bold text-[#DC2626] border border-red-200 animate-bounce">
          <span>⚡ VOICE SWAP SPIKE</span>
        </div>
      )}

      {/* SVG Circular Meter */}
      <div className="relative flex items-center justify-center">
        <svg className="h-48 w-48 transform -rotate-[135deg]" viewBox="0 0 180 180">
          {/* Background Track (Dividers: #ECE8E1) */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke="#ECE8E1"
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
          <div className="text-4xl font-extrabold tracking-tight text-[#1E293B] font-mono">
            {percentage}<span className="text-2xl font-normal text-[#64748B]">%</span>
          </div>
          <span className="text-[11px] uppercase tracking-wider text-[#64748B] mt-0.5 font-medium">
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
        <span className="text-[#15803D] font-semibold">0% Genuine</span>
        <span className="text-[#D97706] font-semibold">30% Caution</span>
        <span className="text-[#D97706] font-semibold">60% Warning</span>
        <span className="text-[#DC2626] font-semibold">80% Critical</span>
      </div>
    </div>
  );
};
