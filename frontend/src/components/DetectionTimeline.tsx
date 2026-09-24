import React, { useState } from 'react';
import { AnalysisUpdate, AnomalyItem } from '../types';
import { AlertTriangle, Radio, ShieldAlert, Globe, Volume2, Sparkles } from 'lucide-react';

interface DetectionTimelineProps {
  timeline: AnalysisUpdate[];
  activeTimestamp: number | null;
  onSeek: (timestampSec: number) => void;
  durationSeconds?: number;
}

export const DetectionTimeline: React.FC<DetectionTimelineProps> = ({
  timeline,
  activeTimestamp,
  onSeek,
  durationSeconds,
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (!timeline || timeline.length === 0) {
    return (
      <div className="p-6 text-center rounded-2xl border border-[#2A2E37] bg-[#15171C] text-[#94A3B8]">
        No temporal detection telemetry available yet.
      </div>
    );
  }

  const hoveredItem = hoveredIndex !== null ? timeline[hoveredIndex] : null;

  return (
    <div className="space-y-4">
      {/* Timeline Controls & Legend */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center space-x-2">
          <span className="font-mono font-bold text-white uppercase tracking-wider text-[11px]">
            Forensic Detection Timeline
          </span>
          <span className="text-[#94A3B8] font-mono text-[10px]">
            ({timeline.length} windows • 1.0s hop • 50% overlap)
          </span>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-3 font-mono text-[10px]">
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
            <span className="text-[#94A3B8]">Authentic Voice</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
            <span className="text-[#94A3B8]">Irregularity / Codec</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#DC2626]" />
            <span className="text-[#94A3B8]">AI Clone / Synthetic</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#8B5CF6]" />
            <span className="text-[#C4B5FD]">Replay Attack</span>
          </div>
        </div>
      </div>

      {/* Threat Ribbon Bar (Continuous Spectrum) */}
      <div className="relative">
        {/* Playhead Marker */}
        {activeTimestamp !== null && (
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-white z-20 pointer-events-none transition-all duration-150 shadow-[0_0_8px_rgba(255,255,255,0.8)]"
            style={{
              left: `${Math.min(
                Math.max(
                  (activeTimestamp / (durationSeconds || (timeline.length * 1.0))) * 100,
                  0
                ),
                100
              )}%`,
            }}
          >
            <div className="w-2 h-2 -ml-[3px] -mt-1 bg-white rotate-45 border border-black" />
          </div>
        )}

        {/* Segmented Scrub Bar */}
        <div className="h-6 w-full flex rounded-lg overflow-hidden border border-[#2A2E37] bg-[#0F1115] shadow-inner cursor-pointer">
          {timeline.map((item, idx) => {
            const isReplay = (item.layer_scores?.replay_attack || 0) >= 0.65 || (item.replay_profile?.replay_probability || 0) >= 0.65;
            let bgColor = '#10B981'; // Green
            if (isReplay) {
              bgColor = '#8B5CF6'; // Purple Replay
            } else if (item.risk_level === 'CRITICAL') {
              bgColor = '#DC2626'; // Deep Red
            } else if (item.risk_level === 'HIGH') {
              bgColor = '#EF4444'; // Red
            } else if (item.risk_level === 'MODERATE') {
              bgColor = '#F59E0B'; // Amber
            }

            const isCurrent = activeTimestamp !== null && Math.abs(activeTimestamp - item.timestamp_sec) < 0.9;

            return (
              <div
                key={idx}
                onClick={() => onSeek(item.timestamp_sec)}
                onMouseEnter={() => setHoveredIndex(idx)}
                onMouseLeave={() => setHoveredIndex(null)}
                className={`flex-1 h-full transition-all duration-150 hover:brightness-130 relative ${
                  isCurrent ? 'ring-1 ring-white' : ''
                }`}
                style={{ backgroundColor: bgColor }}
                title={`${item.timestamp} | Risk: ${Math.round(item.risk_score * 100)}%`}
              />
            );
          })}
        </div>
      </div>

      {/* Scrubbable Amplitude & Anomaly Graph */}
      <div className="h-36 flex items-end space-x-1 p-3 rounded-2xl border overflow-x-auto bg-[#15171C] border-[#252830]">
        {timeline.map((item, idx) => {
          const isReplay = (item.layer_scores?.replay_attack || 0) >= 0.65 || (item.replay_profile?.replay_probability || 0) >= 0.65;
          const heightPercent = Math.max(item.risk_score * 100, 8);

          let barColor = 'bg-[#10B981] hover:bg-[#10B981]/80';
          if (isReplay) barColor = 'bg-[#8B5CF6] hover:bg-[#A78BFA]';
          else if (item.risk_level === 'CRITICAL') barColor = 'bg-[#DC2626] hover:bg-[#DC2626]/80';
          else if (item.risk_level === 'HIGH') barColor = 'bg-[#EF4444] hover:bg-[#EF4444]/80';
          else if (item.risk_level === 'MODERATE') barColor = 'bg-[#F59E0B] hover:bg-[#F59E0B]/80';

          const isSelected = activeTimestamp !== null && Math.abs(activeTimestamp - item.timestamp_sec) < 0.9;
          const hasAnomalies = item.diagnostics && item.diagnostics.length > 0;

          return (
            <button
              key={idx}
              type="button"
              onClick={() => onSeek(item.timestamp_sec)}
              onMouseEnter={() => setHoveredIndex(idx)}
              onMouseLeave={() => setHoveredIndex(null)}
              className="flex-1 flex flex-col items-center group relative min-w-[22px] focus:outline-none h-full justify-end"
            >
              {/* Flag icon if notable anomaly or voice swap */}
              {item.is_spike && (
                <div className="absolute top-0 text-[#EF4444] animate-pulse">
                  <AlertTriangle className="w-3.5 h-3.5" />
                </div>
              )}
              {isReplay && !item.is_spike && (
                <div className="absolute top-0 text-[#8B5CF6]">
                  <Volume2 className="w-3.5 h-3.5" />
                </div>
              )}

              {/* Bar Fill */}
              <div
                className={`w-full rounded-t-sm transition-all cursor-pointer ${barColor} ${
                  isSelected ? 'ring-2 ring-white brightness-125' : ''
                }`}
                style={{ height: `${heightPercent}%` }}
              />

              {/* Timestamp tick label (show every 4th or selected) */}
              {(idx % 4 === 0 || isSelected) && (
                <span
                  className={`text-[8px] font-mono mt-1 ${
                    isSelected ? 'text-white font-bold' : 'text-[#64748B]'
                  }`}
                >
                  {item.timestamp}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Dynamic Hover Inspector Card */}
      {hoveredItem ? (
        <div className="p-4 rounded-2xl border border-[#2A2E37] bg-[#1A1C23] shadow-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#15171C] border border-[#2A2E37] text-white">
              <span className="font-mono font-bold text-xs">{hoveredItem.timestamp}</span>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-bold text-white">
                  Temporal Window #{hoveredItem.window_index} ({hoveredItem.timestamp_sec}s)
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    hoveredItem.risk_level === 'CRITICAL'
                      ? 'bg-[#DC2626]/20 text-[#DC2626] border border-[#DC2626]/30'
                      : hoveredItem.risk_level === 'HIGH'
                      ? 'bg-[#EF4444]/20 text-[#EF4444] border border-[#EF4444]/30'
                      : hoveredItem.risk_level === 'MODERATE'
                      ? 'bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/30'
                      : 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/30'
                  }`}
                >
                  {Math.round(hoveredItem.risk_score * 100)}% Risk ({hoveredItem.risk_level})
                </span>

                {/* Replay Pill */}
                {((hoveredItem.layer_scores?.replay_attack || 0) >= 0.65 ||
                  (hoveredItem.replay_profile?.replay_probability || 0) >= 0.65) && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#8B5CF6]/20 text-[#C4B5FD] border border-[#8B5CF6]/30">
                    Loudspeaker Replay
                  </span>
                )}
              </div>

              {/* Language and Diagnostic note */}
              <div className="flex flex-wrap items-center gap-2 mt-1 text-[11px] text-[#94A3B8]">
                {hoveredItem.language_profile && (
                  <span className="flex items-center space-x-1 text-[#E2E8F0]">
                    <Globe className="w-3 h-3 text-[#10B981]" />
                    <span>{hoveredItem.language_profile.estimated_language}</span>
                  </span>
                )}
                {hoveredItem.diagnostics && hoveredItem.diagnostics.length > 0 ? (
                  <span className="text-[#F59E0B]">
                    • {hoveredItem.diagnostics[0].description}
                  </span>
                ) : (
                  <span className="text-[#10B981]">• Natural vocal fold resonance verified</span>
                )}
              </div>
            </div>
          </div>

          <button
            onClick={() => onSeek(hoveredItem.timestamp_sec)}
            className="text-xs px-3 py-1.5 rounded-xl border font-bold transition-all border-[#2A2E37] bg-[#15171C] hover:border-[#10B981] text-white hover:text-[#10B981]"
          >
            Jump to Second
          </button>
        </div>
      ) : (
        <div className="p-3 text-center rounded-xl border border-[#252830] bg-[#15171C] text-[11px] text-[#64748B]">
          Hover over any point on the timeline to inspect second-by-second acoustic forensics. Click to jump.
        </div>
      )}
    </div>
  );
};
