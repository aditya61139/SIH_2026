import React, { useState, useEffect, useMemo } from 'react';
import { Navbar } from './components/Navbar';
import { LandingView } from './components/LandingView';
import { LiveCallMonitor } from './components/LiveCallMonitor';
import { FileAnalyzer } from './components/FileAnalyzer';
import { ModelTrainingSuite } from './components/ModelTrainingSuite';
import { SettingsPanel } from './components/SettingsPanel';
import { CalibrationModal } from './components/CalibrationModal';
import { VoxSentinalAudioCapture } from './lib/audioCapture';
import { Shield, Sparkles, Cpu, Radio } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'live' | 'upload' | 'train' | 'settings'>('overview');
  const [isCalibrationOpen, setIsCalibrationOpen] = useState<boolean>(false);
  const [wsUrl, setWsUrl] = useState<string>('ws://localhost:8000/ws/analyze');
  const [apiBaseUrl, setApiBaseUrl] = useState<string>('http://localhost:8000');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('vox_theme') as 'dark' | 'light') || 'dark';
  });

  const captureEngine = useMemo(() => new VoxSentinalAudioCapture(), []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    localStorage.setItem('vox_theme', nextTheme);
  };

  // Periodic Backend Health Check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${apiBaseUrl}/api/health`);
        if (res.ok) {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      } catch {
        setIsConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, [apiBaseUrl]);

  const isDark = theme === 'dark';

  return (
    <div className={`min-h-screen flex flex-col transition-colors duration-300 relative ${
      isDark
        ? 'bg-[#070a10] text-slate-100 bg-cyber-grid bg-radial-gradient selection:bg-cyan-500/30 selection:text-cyan-200'
        : 'bg-slate-100 text-slate-900 selection:bg-cyan-500/20 selection:text-cyan-900'
    }`}>
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenCalibration={() => setIsCalibrationOpen(true)}
        isConnected={isConnected}
        isMonitoring={captureEngine.active}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 sm:px-6">
        {activeTab === 'overview' && (
          <LandingView
            onNavigate={setActiveTab}
            onOpenCalibration={() => setIsCalibrationOpen(true)}
            theme={theme}
          />
        )}

        {activeTab === 'live' && (
          <LiveCallMonitor
            captureEngine={captureEngine}
            wsUrl={wsUrl}
            onOpenCalibration={() => setIsCalibrationOpen(true)}
          />
        )}

        {activeTab === 'upload' && (
          <FileAnalyzer apiBaseUrl={apiBaseUrl} theme={theme} />
        )}

        {activeTab === 'train' && (
          <ModelTrainingSuite apiBaseUrl={apiBaseUrl} />
        )}

        {activeTab === 'settings' && (
          <SettingsPanel
            wsUrl={wsUrl}
            setWsUrl={setWsUrl}
            apiBaseUrl={apiBaseUrl}
            setApiBaseUrl={setApiBaseUrl}
          />
        )}
      </main>

      {/* Voiceprint Calibration Modal */}
      <CalibrationModal
        isOpen={isCalibrationOpen}
        onClose={() => setIsCalibrationOpen(false)}
        captureEngine={captureEngine}
        apiBaseUrl={apiBaseUrl}
        theme={theme}
      />

      {/* High-Tech Cyber Footer */}
      <footer className={`border-t py-4 px-6 text-xs transition-colors backdrop-blur-md ${
        isDark ? 'border-slate-800/80 bg-[#070a10]/80 text-slate-400' : 'border-slate-200 bg-white text-slate-600 shadow-inner'
      }`}>
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-cyan-400" />
            <span className={`font-semibold ${isDark ? 'text-slate-300' : 'text-slate-800'}`}>VoxSentinalX</span>
            <span>— Smart India Hackathon Problem Statement #26104</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 text-xs">
            <div className="flex items-center space-x-1.5">
              <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
              <span>8-Vector Forensic Suite</span>
            </div>
            <span className="text-slate-600 hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5">
              <Cpu className="h-3.5 w-3.5 text-violet-400" />
              <span>PyTorch LCNN-BiLSTM</span>
            </div>
            <span className="text-slate-600 hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5">
              <Radio className="h-3.5 w-3.5 text-cyan-400" />
              <span>16 kHz Int16 PCM</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
