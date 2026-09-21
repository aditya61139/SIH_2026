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
    <header className="sticky top-0 z-40 border-b backdrop-blur-xl transition-colors duration-200 border-[#E7E2DA] bg-[#F8F5EF]/95 shadow-xs">
      {/* Patriotic Top Micro-Stripe */}
      <div className="h-1 w-full bg-gradient-to-r from-[#C2410C] via-[#FFFFFF] to-[#15803D]" />

      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5 sm:px-6">
        {/* Brand & Problem Statement ID */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#C2410C] via-amber-500 to-[#15803D] p-0.5 shadow-md shadow-[#C2410C]/10">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-white">
              <Shield className="h-5 w-5 text-[#C2410C]" />
            </div>
            {isMonitoring && (
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#15803D] opacity-75"></span>
                <span className="relative inline-flex h-3 w-3 rounded-full bg-[#15803D]"></span>
              </span>
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold tracking-tight text-[#1E293B]">
                VoxSentinal<span className="text-[#C2410C]">X</span>
              </h1>
              <span className="rounded px-2 py-0.5 text-xs font-semibold border bg-[#FFF1E8] text-[#C2410C] border-[#E7E2DA]">
                SIH 26104
              </span>
            </div>
            <p className="text-xs hidden sm:block text-[#64748B]">
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
                ? 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : 'text-[#64748B] hover:bg-[#EAE5DC] hover:text-[#1E293B]'
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
                ? 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : 'text-[#64748B] hover:bg-[#EAE5DC] hover:text-[#1E293B]'
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
                ? 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : 'text-[#64748B] hover:bg-[#EAE5DC] hover:text-[#1E293B]'
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
                ? 'bg-emerald-50 text-[#15803D] border border-[#15803D]/30 shadow-xs'
                : 'text-[#64748B] hover:bg-[#EAE5DC] hover:text-[#1E293B]'
            }`}
          >
            <Cpu className="h-4 w-4" />
            <span className="hidden md:inline">LCNN Training</span>
          </button>

          {/* Voiceprint Calibration */}
          <button
            onClick={onOpenCalibration}
            className="flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-medium border transition-all bg-white hover:bg-[#FFF1E8] text-[#1E293B] border-[#E7E2DA] shadow-xs"
            title="Calibrate your voice for speakerphone separation"
          >
            <Mic className="h-4 w-4 text-[#15803D]" />
            <span className="hidden lg:inline">Calibration</span>
          </button>

          {/* Settings */}
          <button
            onClick={() => setActiveTab('settings')}
            className={`rounded-xl p-2 text-sm font-medium transition-all ${
              activeTab === 'settings'
                ? 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : 'text-[#64748B] hover:bg-[#EAE5DC] hover:text-[#1E293B]'
            }`}
            title="Settings"
          >
            <SettingsIcon className="h-4 w-4" />
          </button>
        </nav>

        {/* Backend Status Indicator */}
        <div className="hidden xl:flex items-center space-x-2 border-l pl-4 border-[#E7E2DA]">
          <div className="flex items-center space-x-1.5">
            <Radio className={`h-3.5 w-3.5 ${isConnected ? 'text-[#15803D] animate-pulse' : 'text-[#94A3B8]'}`} />
            <span className="text-xs text-[#64748B]">
              Backend: {isConnected ? <span className="text-[#15803D] font-bold">Online (FastAPI)</span> : <span className="text-[#94A3B8]">Offline</span>}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
