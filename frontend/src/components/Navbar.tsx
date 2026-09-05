import React from 'react';
import { Shield, Activity, FileAudio, Settings as SettingsIcon, Mic, Radio, Cpu, Sun, Moon } from 'lucide-react';

interface NavbarProps {
  activeTab: 'live' | 'upload' | 'train' | 'settings';
  setActiveTab: (tab: 'live' | 'upload' | 'train' | 'settings') => void;
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
    <header className={`sticky top-0 z-40 border-b backdrop-blur-md transition-colors ${
      isDark ? 'border-slate-800/80 bg-[#0a0d14]/90' : 'border-slate-200 bg-white/90 shadow-sm'
    }`}>
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Brand & Problem Statement ID */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('live')}>
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-600 to-emerald-400 p-0.5 shadow-lg shadow-cyan-500/20">
            <div className={`flex h-full w-full items-center justify-center rounded-[10px] ${isDark ? 'bg-slate-950' : 'bg-white'}`}>
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
              <h1 className={`text-lg font-bold tracking-tight ${isDark ? 'text-white' : 'text-slate-900'}`}>
                VoxSentinal<span className="text-cyan-400">X</span>
              </h1>
              <span className="rounded bg-cyan-950/80 px-2 py-0.5 text-xs font-semibold text-cyan-300 border border-cyan-800/60">
                SIH 26104
              </span>
            </div>
            <p className={`text-xs hidden sm:block ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              AI-Powered Real-Time Voice Cloning Detection
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab('live')}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === 'live'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Activity className="h-4 w-4" />
            <span className="hidden md:inline">Live Monitor</span>
          </button>

          <button
            onClick={() => setActiveTab('upload')}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === 'upload'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <FileAudio className="h-4 w-4" />
            <span className="hidden md:inline">Audio/MP4 Analyzer</span>
          </button>

          <button
            onClick={() => setActiveTab('train')}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-semibold transition-all ${
              activeTab === 'train'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
            }`}
          >
            <Cpu className="h-4 w-4" />
            <span className="hidden md:inline">Model & Datasets</span>
          </button>

          <button
            onClick={onOpenCalibration}
            className={`flex items-center space-x-1.5 rounded-xl px-3 py-1.5 text-xs sm:text-sm font-medium border transition-all ${
              isDark
                ? 'bg-slate-800/60 hover:bg-slate-700/80 text-slate-300 border-slate-700/60'
                : 'bg-slate-100 hover:bg-slate-200 text-slate-800 border-slate-300'
            }`}
            title="Calibrate your voice for speakerphone separation"
          >
            <Mic className="h-4 w-4 text-emerald-400" />
            <span className="hidden lg:inline">Calibration</span>
          </button>

          <button
            onClick={() => setActiveTab('settings')}
            className={`rounded-xl p-2 text-sm font-medium transition-all ${
              activeTab === 'settings'
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                : isDark
                ? 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
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
                ? 'bg-slate-800/80 text-amber-300 hover:bg-slate-700 border-slate-700 shadow-sm'
                : 'bg-slate-100 text-slate-800 hover:bg-slate-200 border-slate-300 shadow-sm'
            }`}
            title={`Switch to ${isDark ? 'Light' : 'Dark'} Mode`}
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </nav>

        {/* Backend Status Indicator */}
        <div className={`hidden xl:flex items-center space-x-2 border-l pl-4 ${isDark ? 'border-slate-800' : 'border-slate-200'}`}>
          <div className="flex items-center space-x-1.5">
            <Radio className={`h-3.5 w-3.5 ${isConnected ? 'text-emerald-400 animate-pulse' : 'text-slate-400'}`} />
            <span className={`text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
              Backend: {isConnected ? <span className="text-emerald-500 font-bold">Online</span> : <span className="text-slate-400">Offline</span>}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
