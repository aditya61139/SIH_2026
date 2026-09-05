import React, { useState } from 'react';
import { Sliders, Shield, Save, CheckCircle2, Lock, Cpu } from 'lucide-react';

interface SettingsPanelProps {
  wsUrl: string;
  setWsUrl: (url: string) => void;
  apiBaseUrl: string;
  setApiBaseUrl: (url: string) => void;
}

export const SettingsPanel: React.FC<SettingsPanelProps> = ({
  wsUrl,
  setWsUrl,
  apiBaseUrl,
  setApiBaseUrl,
}) => {
  const [localWs, setLocalWs] = useState(wsUrl);
  const [localApi, setLocalApi] = useState(apiBaseUrl);
  const [sensitivity, setSensitivity] = useState<number>(0.75);
  const [autoPurgeMemory, setAutoPurgeMemory] = useState<boolean>(true);
  const [featureOnlyLogging, setFeatureOnlyLogging] = useState<boolean>(true);
  const [saved, setSaved] = useState<boolean>(false);

  const handleSave = () => {
    setWsUrl(localWs);
    setApiBaseUrl(localApi);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="rounded-2xl bg-slate-900/80 p-6 border border-slate-800">
        <div className="flex items-center space-x-3 mb-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
            <Sliders className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">
              System Configuration & Forensic Thresholds
            </h2>
            <p className="text-xs text-slate-400">
              Fine-tune multi-layer detection parameters and compliance policies
            </p>
          </div>
        </div>

        {/* Server Endpoints */}
        <div className="space-y-4 pb-6 border-b border-slate-800">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Backend Engine Endpoints
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-300 font-medium block mb-1">
                WebSocket Streaming URL:
              </label>
              <input
                type="text"
                value={localWs}
                onChange={(e) => setLocalWs(e.target.value)}
                className="w-full rounded-xl bg-slate-950 border border-slate-700 px-3.5 py-2 text-xs font-mono text-cyan-300 focus:border-cyan-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="text-xs text-slate-300 font-medium block mb-1">
                REST API Base URL:
              </label>
              <input
                type="text"
                value={localApi}
                onChange={(e) => setLocalApi(e.target.value)}
                className="w-full rounded-xl bg-slate-950 border border-slate-700 px-3.5 py-2 text-xs font-mono text-cyan-300 focus:border-cyan-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Forensic Sensitivity */}
        <div className="py-6 border-b border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Detection Sensitivity & Rigor
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Controls risk trigger threshold for immediate user alerts
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/80 px-2.5 py-1 rounded-lg border border-cyan-800">
              {Math.round(sensitivity * 100)}% Sensitivity
            </span>
          </div>

          <input
            type="range"
            min="0.4"
            max="0.95"
            step="0.05"
            value={sensitivity}
            onChange={(e) => setSensitivity(parseFloat(e.target.value))}
            className="w-full accent-cyan-400 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>Lenient (Low false positives)</span>
            <span>Balanced (Default)</span>
            <span>Strict (High-security banking)</span>
          </div>
        </div>

        {/* Privacy & DPDP Act 2023 Compliance */}
        <div className="py-6 border-b border-slate-800 space-y-4">
          <div className="flex items-center space-x-2">
            <Lock className="h-4 w-4 text-emerald-400" />
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Privacy & DPDP Act 2023 Compliance Policy
            </h3>
          </div>

          <div className="space-y-3">
            <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800 cursor-pointer">
              <div>
                <span className="text-xs font-bold text-slate-200 block">
                  Zero Audio Storage (In-Memory Processing Only)
                </span>
                <span className="text-[11px] text-slate-400">
                  Audio PCM stream is analyzed in RAM and purged after sliding window completes.
                </span>
              </div>
              <input
                type="checkbox"
                checked={autoPurgeMemory}
                onChange={(e) => setAutoPurgeMemory(e.target.checked)}
                className="h-4 w-4 accent-emerald-500 rounded"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800 cursor-pointer">
              <div>
                <span className="text-xs font-bold text-slate-200 block">
                  Feature-Only Telemetry Logging
                </span>
                <span className="text-[11px] text-slate-400">
                  Only forensic numerical metrics and risk scores are retained for audits.
                </span>
              </div>
              <input
                type="checkbox"
                checked={featureOnlyLogging}
                onChange={(e) => setFeatureOnlyLogging(e.target.checked)}
                className="h-4 w-4 accent-emerald-500 rounded"
              />
            </label>
          </div>
        </div>

        {/* Save Button */}
        <div className="mt-6 flex items-center justify-between">
          <div className="text-xs text-slate-500">
            SIH Problem Statement ID 26104 • VoxSentinalX v1.0.0
          </div>
          <button
            onClick={handleSave}
            className="flex items-center space-x-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 px-5 py-2.5 text-xs font-bold shadow-lg shadow-cyan-500/20 transition-all"
          >
            {saved ? (
              <>
                <CheckCircle2 className="h-4 w-4" />
                <span>Saved Successfully</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Save Settings</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
