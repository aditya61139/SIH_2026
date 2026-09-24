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
  const [wsUrl, setWsUrl] = useState<string>(() => {
    const host = typeof window !== 'undefined' && window.location.hostname ? window.location.hostname : 'localhost';
    const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${host}:8000/ws/analyze`;
  });
  const [apiBaseUrl, setApiBaseUrl] = useState<string>(() => {
    const host = typeof window !== 'undefined' && window.location.hostname ? window.location.hostname : 'localhost';
    const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'https:' : 'http:';
    return `${protocol}//${host}:8000`;
  });
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const captureEngine = useMemo(() => new VoxSentinalAudioCapture(), []);

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
    <div className="min-h-screen flex flex-col bg-[#0D0E11] text-[#E2E8F0] selection:bg-[#10B981]/20 selection:text-[#10B981]">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenCalibration={() => setIsCalibrationOpen(true)}
        isConnected={isConnected}
        isMonitoring={captureEngine.active}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 sm:px-6">
        {activeTab === 'overview' && (
          <LandingView
            onNavigate={setActiveTab}
            onOpenCalibration={() => setIsCalibrationOpen(true)}
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
          <FileAnalyzer apiBaseUrl={apiBaseUrl} />
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
      />

      {/* Cyber-Security Footer */}
      <footer className="border-t border-[#2A2E37] bg-[#0D0E11] py-5 px-6 text-xs text-[#94A3B8] transition-colors">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2.5">
            <div className="h-6 w-6 rounded-md bg-[#1A1C23] border border-[#10B981]/30 p-0.5 overflow-hidden flex items-center justify-center">
              <img src="/Logo.png" alt="VoxSentinalX" className="h-full w-full object-cover rounded-sm" />
            </div>
            <span className="font-semibold text-white">VoxSentinalX</span>
            <span className="text-[#64748B]">— Smart India Hackathon (SIH 2026 • Problem Statement #26104)</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 text-xs">
            <div className="flex items-center space-x-1.5 text-[#94A3B8]">
              <Sparkles className="h-3.5 w-3.5 text-[#10B981]" />
              <span>10-Vector Forensic Suite</span>
            </div>
            <span className="text-[#374151] hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5 text-[#94A3B8]">
              <Cpu className="h-3.5 w-3.5 text-[#10B981]" />
              <span>PyTorch LCNN Neural Classifier</span>
            </div>
            <span className="text-[#374151] hidden sm:inline">•</span>
            <div className="flex items-center space-x-1.5 text-[#94A3B8]">
              <Radio className="h-3.5 w-3.5 text-[#10B981]" />
              <span>16 kHz Streaming Analysis</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
