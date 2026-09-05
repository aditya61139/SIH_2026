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
    <div className="flex flex-col h-full rounded-2xl bg-slate-900/80 p-5 border border-slate-800">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-cyan-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Diagnostic Forensics Feed
          </h3>
        </div>
        <span className="rounded-full bg-slate-800 px-2.5 py-0.5 text-xs text-slate-300 font-mono">
          {anomalies.length} {anomalies.length === 1 ? 'Anomaly' : 'Anomalies'} Detected
        </span>
      </div>

      {/* Primary Message Banner */}
      {userMessage && (
        <div className="mt-4 rounded-xl bg-slate-950/70 p-3.5 border border-slate-800/80">
          <p className="text-xs font-medium text-slate-200 leading-relaxed">
            {userMessage}
          </p>
        </div>
      )}

      {/* Actionable Countermeasure Box */}
      {recommendation && (
        <div className="mt-3 rounded-xl bg-cyan-950/40 p-3.5 border border-cyan-800/50">
          <span className="text-[11px] font-bold text-cyan-400 uppercase tracking-wide">
            Security Recommendation:
          </span>
          <p className="mt-1 text-xs text-cyan-100 font-medium leading-relaxed">
            {recommendation}
          </p>

          {suggestedActions.length > 0 && (
            <ul className="mt-2.5 space-y-1">
              {suggestedActions.map((act, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-[11px] text-cyan-200/90">
                  <span className="text-cyan-400 font-bold">•</span>
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
            <CheckCircle2 className="h-8 w-8 text-emerald-400/60 mb-2" />
            <p className="text-sm font-medium text-slate-400">
              No anomalies detected in audio stream.
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Voice spectrum, respiratory cadence, and prosodic dynamics are natural.
            </p>
          </div>
        ) : (
          anomalies.map((anom, idx) => {
            let badgeBg = 'bg-slate-800 text-slate-300 border-slate-700';
            let Icon = Info;

            if (anom.severity === 'CRITICAL') {
              badgeBg = 'bg-red-500/20 text-red-400 border-red-500/40';
              Icon = AlertCircle;
            } else if (anom.severity === 'HIGH') {
              badgeBg = 'bg-orange-500/20 text-orange-400 border-orange-500/40';
              Icon = AlertTriangle;
            } else if (anom.severity === 'MEDIUM') {
              badgeBg = 'bg-amber-500/20 text-amber-400 border-amber-500/40';
              Icon = AlertTriangle;
            }

            return (
              <div
                key={idx}
                className="rounded-xl bg-slate-950/60 p-3.5 border border-slate-800 hover:border-slate-700 transition-all"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className="h-4 w-4 text-cyan-400" />
                    <span className="text-xs font-bold text-white">
                      {anom.metric_name}
                    </span>
                  </div>
                  <span className={`rounded px-2 py-0.5 text-[10px] font-bold border ${badgeBg}`}>
                    {anom.severity}
                  </span>
                </div>

                <div className="mt-2 grid grid-cols-2 gap-2 text-[11px] font-mono bg-slate-900/60 p-2 rounded-lg border border-slate-800/60">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Measured Value:</span>
                    <span className="text-cyan-300 font-bold">{String(anom.value)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Threshold:</span>
                    <span className="text-slate-300">{anom.threshold}</span>
                  </div>
                </div>

                <p className="mt-2 text-xs text-slate-300 leading-relaxed">
                  {anom.description}
                </p>

                {anom.source_detector && (
                  <div className="mt-2 flex justify-end">
                    <span className="text-[10px] text-slate-400 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
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
