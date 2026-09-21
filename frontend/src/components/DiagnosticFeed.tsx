import React from 'react';
import { AnomalyItem } from '../types';
import { AlertCircle, AlertTriangle, Info, CheckCircle2, ChevronDown } from 'lucide-react';

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
    <div className="flex flex-col h-full rounded-2xl bg-white p-5 border border-[#E7E2DA] shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-[#ECE8E1]">
        <div className="flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-[#C2410C]" />
          <h3 className="text-sm font-bold text-[#1E293B] uppercase tracking-wider">
            Diagnostic Forensics Feed
          </h3>
        </div>
        <span className="rounded-full bg-[#F8F5EF] px-2.5 py-0.5 text-xs text-[#64748B] font-mono border border-[#E7E2DA]">
          {anomalies.length} {anomalies.length === 1 ? 'Anomaly' : 'Anomalies'} Detected
        </span>
      </div>

      {/* Primary Message Banner */}
      {userMessage && (
        <div className="mt-4 rounded-xl bg-[#F8F5EF] p-3.5 border border-[#E7E2DA]">
          <p className="text-xs font-medium text-[#1E293B] leading-relaxed">
            {userMessage}
          </p>
        </div>
      )}

      {/* Actionable Countermeasure Box */}
      {recommendation && (
        <div className="mt-3 rounded-xl bg-[#FFF1E8] p-3.5 border border-[#E7E2DA]">
          <span className="text-[11px] font-bold text-[#C2410C] uppercase tracking-wide">
            Security Recommendation:
          </span>
          <p className="mt-1 text-xs text-[#1E293B] font-medium leading-relaxed">
            {recommendation}
          </p>

          {suggestedActions.length > 0 && (
            <ul className="mt-2.5 space-y-1">
              {suggestedActions.map((act, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-[11px] text-[#1E293B]">
                  <span className="text-[#C2410C] font-bold">•</span>
                  <span>{act}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Scrolling Diagnostic Cards List */}
      <div className="mt-4 flex-1 space-y-3 overflow-y-auto pr-1 max-h-[380px]">
        {anomalies.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <CheckCircle2 className="h-8 w-8 text-[#15803D] mb-2" />
            <p className="text-sm font-medium text-[#1E293B]">
              No anomalies detected in audio stream.
            </p>
            <p className="text-xs text-[#64748B] mt-1">
              Voice spectrum, respiratory cadence, and prosodic dynamics are natural.
            </p>
          </div>
        ) : (
          anomalies.map((anom, idx) => {
            let badgeBg = 'bg-[#F8F5EF] text-[#64748B] border-[#E7E2DA]';
            let Icon = Info;
            let iconColor = 'text-[#C2410C]';

            if (anom.severity === 'CRITICAL') {
              badgeBg = 'bg-red-50 text-[#DC2626] border-red-200 font-bold';
              Icon = AlertCircle;
              iconColor = 'text-[#DC2626]';
            } else if (anom.severity === 'HIGH') {
              badgeBg = 'bg-red-50 text-[#DC2626] border-red-200 font-bold';
              Icon = AlertTriangle;
              iconColor = 'text-[#DC2626]';
            } else if (anom.severity === 'MEDIUM') {
              badgeBg = 'bg-amber-50 text-[#D97706] border-amber-200 font-bold';
              Icon = AlertTriangle;
              iconColor = 'text-[#D97706]';
            }

            return (
              <div
                key={idx}
                className="rounded-xl bg-[#F8F5EF] p-3.5 border border-[#E7E2DA] hover:border-[#C2410C]/40 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className={`h-4 w-4 ${iconColor}`} />
                    <span className="text-xs font-bold text-[#1E293B]">
                      {anom.metric_name}
                    </span>
                  </div>
                  <span className={`rounded px-2 py-0.5 text-[10px] font-bold border ${badgeBg}`}>
                    {anom.severity}
                  </span>
                </div>

                <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] font-mono bg-white p-2 rounded-lg border border-[#E7E2DA]">
                  <div>
                    <span className="text-[#64748B] block text-[10px]">Measured Value:</span>
                    <span className="text-[#C2410C] font-bold">{String(anom.value)}</span>
                  </div>
                  <div>
                    <span className="text-[#64748B] block text-[10px]">Threshold:</span>
                    <span className="text-[#1E293B] font-medium">{anom.threshold}</span>
                  </div>
                </div>

                <p className="mt-2 text-xs text-[#64748B] leading-relaxed">
                  {anom.description}
                </p>

                {anom.source_detector && (
                  <div className="mt-2 flex justify-end">
                    <span className="text-[10px] text-[#64748B] font-mono bg-white px-2 py-0.5 rounded border border-[#E7E2DA]">
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
