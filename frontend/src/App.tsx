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
  const [theme, setTheme] = useState<'dark' | 'light'>('light');

  const captureEngine = useMemo(() => new VoxSentinalAudioCapture(), []);

  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
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

  return (
    <div className="min-h-screen flex flex-col bg-[#FDFBF7] text-[#1E293B] selection:bg-[#FFF1E8] selection:text-[#C2410C]">
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

      {/* Swadesi Footer */}
      <footer className="border-t border-[#E7E2DA] bg-[#F8F5EF] py-5 px-6 text-xs text-[#64748B] transition-colors">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 rounded-full bg-[#15803D]"></div>
            <span className="font-semibold text-[#1E293B]">VoxSentinalX</span>
            <span>— Smart India Hackathon (SIH 2026 • Problem Statement #26104)</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 text-xs">
            <div className="flex items-center space-x-1.5 text-[#64748B]">
              <Sparkles className="h-3.5 w-3.5 text-[#C2410C]" />
              <span>8-Vector Forensic Suite</span>
            </div>
            <span className="text-[#CBD5E1] hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5 text-[#64748B]">
              <Cpu className="h-3.5 w-3.5 text-[#15803D]" />
              <span>PyTorch LCNN Neural Classifier</span>
            </div>
            <span className="text-[#CBD5E1] hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5 text-[#64748B]">
              <Radio className="h-3.5 w-3.5 text-[#C2410C]" />
              <span>16 kHz Streaming Analysis</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
