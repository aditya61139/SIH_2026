import React from 'react';
import { AnomalyItem } from '../types';
import { AlertCircle, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

interface DiagnosticFeedProps {
  anomalies: AnomalyItem[];
  userMessage?: string;
  recommendation?: string;
  suggestedActions?: string[];
}

export const DiagnosticFeed: React.FC<DiagnosticFeedProps> = ({
  anomalies,
  userMessage,
  recommendation,
  suggestedActions = [],
}) => {
  return (
    <div className="flex flex-col h-full rounded-2xl bg-[#1A1C23] p-5 border border-[#2A2E37] shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-[#252830]">
        <div className="flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-[#10B981]" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Diagnostic Forensics Feed
          </h3>
        </div>
        <span className="rounded-full bg-[#15171C] px-2.5 py-0.5 text-xs text-[#94A3B8] font-mono border border-[#2A2E37]">
          {anomalies.length} {anomalies.length === 1 ? 'Anomaly' : 'Anomalies'} Detected
        </span>
      </div>

      {/* Primary Message Banner */}
      {userMessage && (
        <div className="mt-4 rounded-xl bg-[#15171C] p-3.5 border border-[#2A2E37]">
          <p className="text-xs font-medium text-[#E2E8F0] leading-relaxed">
            {userMessage}
          </p>
        </div>
      )}

      {/* Actionable Countermeasure Box */}
      {recommendation && (
        <div className="mt-3 rounded-xl bg-[#10B981]/10 p-3.5 border border-[#10B981]/30">
          <span className="text-[11px] font-bold text-[#10B981] uppercase tracking-wide">
            Security Recommendation:
          </span>
          <p className="mt-1 text-xs text-[#E2E8F0] font-medium leading-relaxed">
            {recommendation}
          </p>

          {suggestedActions.length > 0 && (
            <ul className="mt-2.5 space-y-1">
              {suggestedActions.map((act, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-[11px] text-[#E2E8F0]">
                  <span className="text-[#10B981] font-bold">•</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Scrolling Diagnostic Cards List */}
      <div className="mt-4 flex-1 space-y-3 overflow-y-auto pr-1 max-h-[340px]">
        {anomalies.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <CheckCircle2 className="h-8 w-8 text-[#10B981] mb-2" />
            <p className="text-sm font-medium text-white">
              No anomalies detected in audio stream.
            </p>
            <p className="text-xs text-[#94A3B8] mt-1">
              Voice spectrum, respiratory cadence, and prosodic dynamics are natural.
            </p>
          </div>
        ) : (
          anomalies.map((anom, idx) => {
            let badgeBg = 'bg-[#15171C] text-[#94A3B8] border-[#2A2E37]';
            let Icon = Info;
            let iconColor = 'text-[#10B981]';

            if (anom.severity === 'CRITICAL') {
              badgeBg = 'bg-[#DC2626]/20 text-[#DC2626] border-[#DC2626]/40 font-bold';
              Icon = AlertCircle;
              iconColor = 'text-[#DC2626]';
            } else if (anom.severity === 'HIGH') {
              badgeBg = 'bg-[#EF4444]/15 text-[#EF4444] border-[#EF4444]/30 font-bold';
              Icon = AlertTriangle;
              iconColor = 'text-[#EF4444]';
            } else if (anom.severity === 'MEDIUM') {
              badgeBg = 'bg-[#F59E0B]/15 text-[#F59E0B] border-[#F59E0B]/30 font-bold';
              Icon = AlertTriangle;
              iconColor = 'text-[#F59E0B]';
            }

            return (
              <div
                key={idx}
                className="rounded-xl bg-[#15171C] p-3.5 border border-[#2A2E37] hover:border-[#374151] transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className={`h-4 w-4 ${iconColor}`} />
                    <span className="text-xs font-bold text-white">
                      {anom.metric_name}
                    </span>
                  </div>
                  <span className={`rounded px-2 py-0.5 text-[10px] font-bold border ${badgeBg}`}>
                    {anom.severity}
                  </span>
                </div>

                <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] font-mono bg-[#1A1C23] p-2 rounded-lg border border-[#252830]">
                  <div>
                    <span className="text-[#64748B] block text-[10px]">Measured Value:</span>
                    <span className="text-[#10B981] font-bold">{String(anom.value)}</span>
                  </div>
                  <div>
                    <span className="text-[#64748B] block text-[10px]">Threshold:</span>
                    <span className="text-[#94A3B8] font-medium">{anom.threshold}</span>
                  </div>
                </div>

                <p className="mt-2 text-xs text-[#94A3B8] leading-relaxed">
                  {anom.description}
                </p>

                {anom.source_detector && (
                  <div className="mt-2 flex justify-end">
                    <span className="text-[10px] text-[#94A3B8] font-mono bg-[#1A1C23] px-2 py-0.5 rounded border border-[#2A2E37]">
                      Layer: {anom.source_detector}
                    </span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
