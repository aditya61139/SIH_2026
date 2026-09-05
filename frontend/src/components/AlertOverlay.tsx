import React from 'react';
import { ShieldAlert, PhoneOff, Lock, FileDown, X } from 'lucide-react';
import { AnomalyItem } from '../types';

interface AlertOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  riskScore: number;
  anomalies: AnomalyItem[];
  recommendation: string;
}

export const AlertOverlay: React.FC<AlertOverlayProps> = ({
  isOpen,
  onClose,
  riskScore,
  anomalies,
  recommendation,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl rounded-2xl bg-slate-950 border-2 border-red-500/80 p-6 shadow-2xl shadow-red-500/30">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header with Pulsing Alert Icon */}
        <div className="flex items-center space-x-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-500/20 border border-red-500/40 animate-pulse">
            <ShieldAlert className="h-7 w-7 text-red-500" />
          </div>
          <div>
            <span className="rounded bg-red-500/30 px-2 py-0.5 text-[11px] font-bold text-red-300 uppercase tracking-wider border border-red-500/40">
              Immediate Security Threat
            </span>
            <h2 className="text-xl font-extrabold text-white mt-0.5">
              High Probability AI Voice Clone Detected!
            </h2>
          </div>
        </div>

        {/* Risk Score Pill */}
        <div className="mt-4 flex items-center justify-between rounded-xl bg-red-950/40 p-3.5 border border-red-900/60">
          <div>
            <span className="text-xs text-red-300 font-medium">Confidence Rating:</span>
            <div className="text-2xl font-mono font-extrabold text-red-400">
              {Math.round(riskScore * 100)}% Synthetic
            </div>
          </div>
          <div className="text-right text-xs text-slate-300">
            <div>Multi-Layer Verification: <span className="text-red-400 font-bold">FAILED</span></div>
            <div>Acoustic Resonances: <span className="text-red-400 font-bold">ANOMALOUS</span></div>
          </div>
        </div>

        {/* Security Recommendation */}
        <div className="mt-4">
          <h4 className="text-xs font-bold text-red-400 uppercase tracking-wide">
            Actionable Directive:
          </h4>
          <p className="mt-1 text-sm text-slate-200 bg-slate-900/90 p-3 rounded-xl border border-slate-800 font-medium">
            {recommendation || 'Do not authorize financial transfers or release sensitive access credentials. Initiate immediate callback verification.'}
          </p>
        </div>

        {/* Detected Signatures */}
        <div className="mt-3">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wide">
            Forensic Signatures Identified:
          </h4>
          <div className="mt-1.5 space-y-1.5 max-h-28 overflow-y-auto pr-1">
            {anomalies.slice(0, 3).map((a, i) => (
              <div key={i} className="text-xs text-slate-300 flex items-start space-x-2 bg-slate-900/50 p-2 rounded-lg">
                <span className="text-red-400 font-bold">•</span>
                <span><strong>{a.metric_name}:</strong> {a.description}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Countermeasure Action Buttons */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-4 border-t border-slate-800">
          <button
            onClick={() => {
              alert('Callback Verification Triggered: Please call the contact on their pre-registered phone number.');
            }}
            className="flex items-center justify-center space-x-1.5 rounded-xl bg-red-600 hover:bg-red-500 py-2.5 px-3 text-xs font-bold text-white shadow-lg shadow-red-600/30 transition-all"
          >
            <Lock className="h-4 w-4" />
            <span>Verify Identity</span>
          </button>

          <button
            onClick={() => {
              const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ riskScore, anomalies, timestamp: new Date().toISOString() }, null, 2));
              const downloadAnchor = document.createElement('a');
              downloadAnchor.setAttribute("href", dataStr);
              downloadAnchor.setAttribute("download", `VoxSentinalX_Forensic_Incident_${Date.now()}.json`);
              document.body.appendChild(downloadAnchor);
              downloadAnchor.click();
              downloadAnchor.remove();
            }}
            className="flex items-center justify-center space-x-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 py-2.5 px-3 text-xs font-bold text-slate-200 border border-slate-700 transition-all"
          >
            <FileDown className="h-4 w-4 text-cyan-400" />
            <span>Export Log</span>
          </button>

          <button
            onClick={onClose}
            className="flex items-center justify-center space-x-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 py-2.5 px-3 text-xs font-semibold text-slate-400 border border-slate-800 transition-all"
          >
            <span>Acknowledge</span>
          </button>
        </div>
      </div>
    </div>
  );
};
