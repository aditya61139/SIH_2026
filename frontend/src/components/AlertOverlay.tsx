import React from 'react';
import { ShieldAlert, Lock, FileDown, X } from 'lucide-react';
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
      <div className="relative w-full max-w-xl rounded-2xl bg-[#1A1C23] border-2 border-[#EF4444] p-6 shadow-2xl shadow-red-500/20">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#94A3B8] hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Header with Pulsing Alert Icon */}
        <div className="flex items-center space-x-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#EF4444]/15 border border-[#EF4444]/40 animate-pulse">
            <ShieldAlert className="h-7 w-7 text-[#EF4444]" />
          </div>
          <div>
            <span className="rounded bg-[#EF4444]/20 px-2 py-0.5 text-[11px] font-bold text-[#EF4444] uppercase tracking-wider border border-[#EF4444]/40">
              Immediate Security Threat
            </span>
            <h2 className="text-xl font-extrabold text-white mt-0.5">
              High Probability AI Voice Clone Detected!
            </h2>
          </div>
        </div>

        {/* Risk Score Pill */}
        <div className="mt-4 flex items-center justify-between rounded-xl bg-[#EF4444]/15 p-3.5 border border-[#EF4444]/40">
          <div>
            <span className="text-xs text-[#EF4444] font-medium">Confidence Rating:</span>
            <div className="text-2xl font-mono font-extrabold text-[#EF4444]">
              {Math.round(riskScore * 100)}% Synthetic
            </div>
          </div>
          <div className="text-right text-xs text-[#94A3B8]">
            <div>Multi-Layer Verification: <span className="text-[#EF4444] font-bold">FAILED</span></div>
            <div>Acoustic Resonances: <span className="text-[#EF4444] font-bold">ANOMALOUS</span></div>
          </div>
        </div>

        {/* Security Recommendation */}
        <div className="mt-4">
          <h4 className="text-xs font-bold text-[#EF4444] uppercase tracking-wide">
            Actionable Directive:
          </h4>
          <p className="mt-1 text-sm text-[#E2E8F0] bg-[#15171C] p-3 rounded-xl border border-[#2A2E37] font-medium">
            {recommendation || 'Do not authorize financial transfers or release sensitive access credentials. Initiate immediate callback verification.'}
          </p>
        </div>

        {/* Detected Signatures */}
        <div className="mt-3">
          <h4 className="text-xs font-bold text-[#94A3B8] uppercase tracking-wide">
            Forensic Signatures Identified:
          </h4>
          <div className="mt-1.5 space-y-1.5 max-h-28 overflow-y-auto pr-1">
            {anomalies.slice(0, 3).map((a, i) => (
              <div key={i} className="text-xs text-[#E2E8F0] flex items-start space-x-2 bg-[#15171C] p-2 rounded-lg border border-[#2A2E37]">
                <span className="text-[#EF4444] font-bold">•</span>
                <span><strong>{a.metric_name}:</strong> {a.description}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Countermeasure Action Buttons */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-4 border-t border-[#252830]">
          <button
            onClick={() => {
              alert('Callback Verification Triggered: Please call the contact on their pre-registered phone number.');
            }}
            className="flex items-center justify-center space-x-1.5 rounded-xl bg-[#EF4444] hover:bg-red-700 py-2.5 px-3 text-xs font-bold text-white shadow-md shadow-red-600/30 transition-all"
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
            className="flex items-center justify-center space-x-1.5 rounded-xl bg-[#15171C] hover:bg-[#10B981]/10 py-2.5 px-3 text-xs font-bold text-[#10B981] border border-[#2A2E37] transition-all"
          >
            <FileDown className="h-4 w-4 text-[#10B981]" />
            <span>Export Log</span>
          </button>

          <button
            onClick={onClose}
            className="flex items-center justify-center space-x-1.5 rounded-xl bg-[#15171C] hover:bg-[#1A1C23] py-2.5 px-3 text-xs font-semibold text-[#94A3B8] hover:text-white border border-[#2A2E37] transition-all"
          >
            <span>Acknowledge</span>
          </button>
        </div>
      </div>
    </div>
  );
};
