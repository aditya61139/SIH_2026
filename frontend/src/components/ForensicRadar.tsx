import React from 'react';
import { LayerScores, RiskLevel } from '../types';

interface ForensicRadarProps {
  scores: LayerScores;
  riskLevel: RiskLevel;
}

export const ForensicRadar: React.FC<ForensicRadarProps> = ({ scores, riskLevel }) => {
  const axes = [
    { key: 'spectral', label: 'Spectral' },
    { key: 'prosody', label: 'Prosody' },
    { key: 'breathing', label: 'Breathing' },
    { key: 'acoustic_artifacts', label: 'Vocoder' },
    { key: 'lfcc', label: 'LFCC' },
    { key: 'glottal', label: 'Glottal' },
    { key: 'perturbation', label: 'Jitter/Shimmer' },
    { key: 'bispectrum', label: 'Bispectrum' },
  ];

  const size = 260;
  const center = size / 2;
  const radius = 90;
  const numAxes = axes.length;

  // Compute vertices for concentric grid circles
  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  // Compute active data polygon points
  const points = axes.map((axis, i) => {
    const angle = (i * 2 * Math.PI) / numAxes - Math.PI / 2;
    const scoreVal = Math.min(Math.max((scores as any)[axis.key] || 0, 0.05), 1.0);
    const r = scoreVal * radius;
    const x = center + r * Math.cos(angle);
    const y = center + r * Math.sin(angle);
    return `${x},${y}`;
  }).join(' ');

  let strokeColor = '#10B981'; // Low risk / genuine (#10B981)
  let fillColor = 'rgba(16, 185, 129, 0.20)';

  if (riskLevel === 'CRITICAL') {
    strokeColor = '#DC2626'; // Critical Error (#DC2626)
    fillColor = 'rgba(220, 38, 38, 0.32)';
  } else if (riskLevel === 'HIGH') {
    strokeColor = '#EF4444'; // High Risk / Clone Detected (#EF4444)
    fillColor = 'rgba(239, 68, 68, 0.25)';
  } else if (riskLevel === 'MODERATE') {
    strokeColor = '#F59E0B'; // Medium Risk / Suspicious (#F59E0B)
    fillColor = 'rgba(245, 158, 11, 0.22)';
  }

  return (
    <div className="flex flex-col items-center justify-center p-3">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="overflow-visible">
        {/* Concentric Grid Octagons (Standard Border: #2A2E37) */}
        {gridLevels.map((lvl, idx) => {
          const gridPts = axes.map((_, i) => {
            const angle = (i * 2 * Math.PI) / numAxes - Math.PI / 2;
            const r = lvl * radius;
            const x = center + r * Math.cos(angle);
            const y = center + r * Math.sin(angle);
            return `${x},${y}`;
          }).join(' ');

          return (
            <polygon
              key={idx}
              points={gridPts}
              fill="none"
              stroke="#2A2E37"
              strokeWidth="1"
              strokeDasharray={lvl < 1.0 ? "2 2" : "none"}
            />
          );
        })}

        {/* Axis Lines & Labels (Divider: #252830) */}
        {axes.map((axis, i) => {
          const angle = (i * 2 * Math.PI) / numAxes - Math.PI / 2;
          const x = center + radius * Math.cos(angle);
          const y = center + radius * Math.sin(angle);
          const labelX = center + (radius + 20) * Math.cos(angle);
          const labelY = center + (radius + 15) * Math.sin(angle);

          return (
            <g key={i}>
              <line
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="#252830"
                strokeWidth="1"
              />
              <text
                x={labelX}
                y={labelY}
                textAnchor="middle"
                dominantBaseline="middle"
                className="text-[9px] font-mono fill-[#94A3B8] font-semibold"
              >
                {axis.label}
              </text>
            </g>
          );
        })}

        {/* Active Anomaly Radar Polygon */}
        <polygon
          points={points}
          fill={fillColor}
          stroke={strokeColor}
          strokeWidth="2"
          className="transition-all duration-300 ease-out"
        />

        {/* Vertices Dots */}
        {axes.map((axis, i) => {
          const angle = (i * 2 * Math.PI) / numAxes - Math.PI / 2;
          const scoreVal = Math.min(Math.max((scores as any)[axis.key] || 0, 0.05), 1.0);
          const r = scoreVal * radius;
          const x = center + r * Math.cos(angle);
          const y = center + r * Math.sin(angle);

          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="3.5"
              fill={strokeColor}
              className="transition-all duration-300"
            />
          );
        })}
      </svg>
      <span className="text-[10px] font-mono uppercase text-[#64748B] tracking-wider mt-1 font-medium">
        8-Axis Forensic Radar
      </span>
    </div>
  );
};
