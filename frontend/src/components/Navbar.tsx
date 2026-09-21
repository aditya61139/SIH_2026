import React from 'react';
import { Shield, Activity, FileAudio, Settings as SettingsIcon, Mic, Radio, Cpu, Sun, Moon, LayoutGrid, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: 'overview' | 'live' | 'upload' | 'train' | 'settings';
  setActiveTab: (tab: 'overview' | 'live' | 'upload' | 'train' | 'settings') => void;
  onOpenCalibration: () => void;
  isConnected: boolean;
  isMonitoring: boolean;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  onOpenCalibration,
  isConnected,
  isMonitoring,
  theme,
  onToggleTheme,
}) => {
  const isDark = theme === 'dark';

  return (
    <header className={`sticky top-0 z-40 border-b backdrop-blur-xl transition-colors duration-200 ${
      isDark ? 'border-slate-800/80 bg-[#070a10]/90' : 'border-[#E7E2DA] bg-[#F8F5EF]/95 shadow-xs'
    }`}>
      {/* Patriotic Top Micro-Stripe */}
      <div className="h-1 w-full bg-gradient-to-r from-[#C2410C] via-[#FFFFFF] to-[#15803D]" />

      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-2.5 sm:px-6">
        {/* Brand & Problem Statement ID */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('overview')}>
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-[#C2410C] via-amber-500 to-[#15803D] p-0.5 shadow-md shadow-[#C2410C]/10">
            <div className={`flex h-full w-full items-center justify-center rounded-[10px] ${isDark ? 'bg-slate-950' : 'bg-white'}`}>
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
              <h1 className={`text-lg font-bold tracking-tight ${isDark ? 'text-white' : 'text-[#1E293B]'}`}>
                VoxSentinal<span className="text-[#C2410C]">X</span>
              </h1>
              <span className={`rounded px-2 py-0.5 text-xs font-semibold border ${
                isDark
                  ? 'bg-orange-950/80 text-orange-300 border-orange-800/60'
                  : 'bg-[#FFF1E8] text-[#C2410C] border-[#E7E2DA]'
              }`}>
                SIH 26104
              </span>
            </div>
            <p className={`text-xs hidden sm:block ${isDark ? 'text-slate-400' : 'text-[#64748B]'}`}>
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
                ? isDark
                  ? 'bg-[#C2410C]/20 text-orange-300 border border-[#C2410C]/40'
                  : 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
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
                ? isDark
                  ? 'bg-[#C2410C]/20 text-orange-300 border border-[#C2410C]/40'
                  : 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
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
                ? isDark
                  ? 'bg-[#C2410C]/20 text-orange-300 border border-[#C2410C]/40'
                  : 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
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
                ? isDark
                  ? 'bg-[#15803D]/25 text-emerald-300 border border-[#15803D]/50'
                  : 'bg-emerald-50 text-[#15803D] border border-[#15803D]/30 shadow-xs'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                : 'text-[#64748B] hover:bg-[#EAE5DC] hover:text-[#1E293B]'
            }`}
          >
            <Cpu className="h-4 w-4" />
            <span className="hidden md:inline">LCNN Training</span>
          </button>

          {/* Voiceprint Calibration */}
          <button
            onClick={onOpenCalibration}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-medium border transition-all ${
              isDark
                ? 'bg-slate-900/80 hover:bg-slate-800 text-slate-300 border-slate-700/80'
                : 'bg-white hover:bg-[#FFF1E8] text-[#1E293B] border-[#E7E2DA] shadow-xs'
            }`}
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
                ? isDark
                  ? 'bg-[#C2410C]/20 text-orange-300 border border-[#C2410C]/40'
                  : 'bg-[#FFF1E8] text-[#C2410C] border border-[#C2410C]/30 shadow-xs'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                : 'text-[#64748B] hover:bg-[#EAE5DC] hover:text-[#1E293B]'
            }`}
            title="Settings"
          >
            <SettingsIcon className="h-4 w-4" />
          </button>

          {/* Theme Toggle Button (Light / Dark) */}
          <button
            onClick={onToggleTheme}
            className={`rounded-xl p-2 text-sm font-medium border transition-all ${
              isDark
                ? 'bg-slate-900/90 text-amber-300 hover:bg-slate-800 border-slate-800 shadow-sm'
                : 'bg-white text-[#64748B] hover:bg-[#F8F5EF] hover:text-[#1E293B] border-[#E7E2DA] shadow-xs'
            }`}
            title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </nav>

        {/* Backend Status Indicator */}
        <div className={`hidden xl:flex items-center space-x-2 border-l pl-4 ${isDark ? 'border-slate-800' : 'border-[#E7E2DA]'}`}>
          <div className="flex items-center space-x-1.5">
            <Radio className={`h-3.5 w-3.5 ${isConnected ? 'text-[#15803D] animate-pulse' : 'text-[#94A3B8]'}`} />
            <span className={`text-xs ${isDark ? 'text-slate-400' : 'text-[#64748B]'}`}>
              Backend: {isConnected ? <span className="text-[#15803D] font-bold">Online (FastAPI)</span> : <span className="text-[#94A3B8]">Offline</span>}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
