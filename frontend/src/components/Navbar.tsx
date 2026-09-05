import React from 'react';
import { Shield, Activity, FileAudio, Settings as SettingsIcon, Mic, Radio } from 'lucide-react';

interface NavbarProps {
  activeTab: 'live' | 'upload' | 'settings';
  setActiveTab: (tab: 'live' | 'upload' | 'settings') => void;
  onOpenCalibration: () => void;
  isConnected: boolean;
  isMonitoring: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenCalibration,
  isConnected,
  isMonitoring,
}) => {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-[#0a0d14]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand & Problem Statement ID */}
        <div className="flex items-center space-x-3">
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-400 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-slate-950">
              <Shield className="h-5 w-5 text-cyan-400" />
            </div>
            {isMonitoring && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-500"></span>
              </span>
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold tracking-tight text-white">
                VoxSentinal<span className="text-cyan-400">X</span>
              </h1>
              <span className="rounded bg-cyan-950/80 px-2 py-0.5 text-xs font-semibold text-cyan-300 border border-cyan-800/60">
                SIH 26104
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              AI-Powered Real-Time Voice Cloning Detection & Prevention
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('live')}
            className={`flex items-center space-x-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
              activeTab === 'live'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
            }`}
          >
            <Activity className="h-4 w-4" />
            <span>Live Monitor</span>
          </button>

          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center space-x-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${
              activeTab === 'upload'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
            }`}
          >
            <FileAudio className="h-4 w-4" />
            <span>File Analyzer</span>
          </button>

          <button
            onClick={onOpenCalibration}
            className="flex items-center space-x-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-slate-300 bg-slate-800/60 hover:bg-slate-700/80 border border-slate-700/60 transition-all"
            title="Calibrate your voice for speaker separation"
          >
            <Mic className="h-4 w-4 text-emerald-400" />
            <span className="hidden md:inline">Voiceprint Calibration</span>
          </button>

          <button
            onClick={() => setActiveTab('settings')}
            className={`flex items-center space-x-1.5 rounded-lg p-2 text-sm font-medium transition-all ${
              activeTab === 'settings'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
            }`}
            title="Settings"
          >
            <SettingsIcon className="h-4 w-4" />
          </button>
        </nav>

        {/* Backend Status Indicator */}
        <div className="hidden lg:flex items-center space-x-2 border-l border-slate-800 pl-4">
          <div className="flex items-center space-x-1.5">
            <Radio className={`h-3.5 w-3.5 ${isConnected ? 'text-emerald-400 animate-pulse' : 'text-slate-500'}`} />
            <span className="text-xs text-slate-400">
              Backend: {isConnected ? <span className="text-emerald-400 font-medium">Online</span> : <span className="text-slate-500">Disconnected</span>}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
