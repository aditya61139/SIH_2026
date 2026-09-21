import React from 'react';
import { Shield, Activity, FileAudio, Settings as SettingsIcon, Mic, Radio, Cpu, LayoutGrid } from 'lucide-react';

interface NavbarProps {
  activeTab: 'overview' | 'live' | 'upload' | 'train' | 'settings';
  setActiveTab: (tab: 'overview' | 'live' | 'upload' | 'train' | 'settings') => void;
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
    <header className="sticky top-0 z-40 border-b backdrop-blur-xl transition-colors duration-200 border-[#2A2E37] bg-[#0D0E11]/95 shadow-lg shadow-black/40">
      {/* Top Cyber Accent Micro-Stripe */}
      <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-[#10B981] to-transparent" />

      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5 sm:px-6">
        {/* Brand & Problem Statement ID */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#10B981] via-emerald-600 to-[#1A1C23] p-0.5 shadow-md shadow-[#10B981]/20">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#1A1C23]">
              <Shield className="h-5 w-5 text-[#10B981]" />
            </div>
            {isMonitoring && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#10B981] opacity-75"></span>
                <span className="relative inline-flex h-3 w-3 rounded-full bg-[#10B981]"></span>
              </span>
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold tracking-tight text-white">
                VoxSentinal<span className="text-[#10B981]">X</span>
              </h1>
              <span className="rounded px-2 py-0.5 text-xs font-semibold border bg-[#10B981]/10 text-[#10B981] border-[#10B981]/30">
                SIH 26104
              </span>
            </div>
            <p className="text-xs hidden sm:block text-[#94A3B8]">
              AI Voice Cloning Defense & Acoustic Forensics
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-1.5">
          {/* Overview / Showcase Tab */}
          <button
            onClick={() => setActiveTab('overview')}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === 'overview'
                ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 shadow-xs'
                : 'text-[#94A3B8] hover:bg-[#15171C] hover:text-white'
            }`}
          >
            <LayoutGrid className="h-4 w-4" />
            <span className="hidden md:inline">Showcase</span>
          </button>

          {/* Live Monitor */}
          <button
            onClick={() => setActiveTab('live')}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === 'live'
                ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 shadow-xs'
                : 'text-[#94A3B8] hover:bg-[#15171C] hover:text-white'
            }`}
          >
            <Activity className="h-4 w-4" />
            <span className="hidden md:inline">Live Monitor</span>
          </button>

          {/* File Analyzer */}
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === 'upload'
                ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 shadow-xs'
                : 'text-[#94A3B8] hover:bg-[#15171C] hover:text-white'
            }`}
          >
            <FileAudio className="h-4 w-4" />
            <span className="hidden md:inline">File Analyzer</span>
          </button>

          {/* Model Suite */}
          <button
            onClick={() => setActiveTab('train')}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === 'train'
                ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 shadow-xs'
                : 'text-[#94A3B8] hover:bg-[#15171C] hover:text-white'
            }`}
          >
            <Cpu className="h-4 w-4" />
            <span className="hidden md:inline">LCNN Training</span>
          </button>

          {/* Voiceprint Calibration */}
          <button
            onClick={onOpenCalibration}
            className="flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-medium border transition-all bg-[#1A1C23] hover:bg-[#10B981]/10 text-[#E2E8F0] hover:text-[#10B981] border-[#2A2E37] shadow-xs"
            title="Calibrate your voice for speakerphone separation"
          >
            <Mic className="h-4 w-4 text-[#10B981]" />
            <span className="hidden lg:inline">Calibration</span>
          </button>

          {/* Settings */}
          <button
            onClick={() => setActiveTab('settings')}
            className={`rounded-xl p-2 text-sm font-medium transition-all ${
              activeTab === 'settings'
                ? 'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 shadow-xs'
                : 'text-[#94A3B8] hover:bg-[#15171C] hover:text-white'
            }`}
            title="Settings"
          >
            <SettingsIcon className="h-4 w-4" />
          </button>
        </nav>

        {/* Backend Status Indicator */}
        <div className="hidden xl:flex items-center space-x-2 border-l pl-4 border-[#2A2E37]">
          <div className="flex items-center space-x-1.5">
            <Radio className={`h-3.5 w-3.5 ${isConnected ? 'text-[#10B981] animate-pulse' : 'text-[#64748B]'}`} />
            <span className="text-xs text-[#94A3B8]">
              Backend: {isConnected ? <span className="text-[#10B981] font-bold">Online (FastAPI)</span> : <span className="text-[#64748B]">Offline</span>}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
