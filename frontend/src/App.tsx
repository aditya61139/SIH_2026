import React, { useState, useEffect, useMemo } from 'react';
import { Navbar } from './components/Navbar';
import { LiveCallMonitor } from './components/LiveCallMonitor';
import { FileAnalyzer } from './components/FileAnalyzer';
import { SettingsPanel } from './components/SettingsPanel';
import { CalibrationModal } from './components/CalibrationModal';
import { VoxSentinalAudioCapture } from './lib/audioCapture';
import { Shield, Sparkles } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'live' | 'upload' | 'settings'>('live');
  const [isCalibrationOpen, setIsCalibrationOpen] = useState<boolean>(false);
  const [wsUrl, setWsUrl] = useState<string>('ws://localhost:8000/ws/analyze');
  const [apiBaseUrl, setApiBaseUrl] = useState<string>('http://localhost:8000');
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
    <div className="min-h-screen flex flex-col bg-[#0a0d14] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
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
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-4 px-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-cyan-400" />
            <span className="font-semibold text-slate-300">VoxSentinalX</span>
            <span>— Smart India Hackathon Problem Statement #26104</span>
          </div>
          <div className="flex items-center space-x-1.5 text-slate-400">
            <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
            <span>Multi-Layer Acoustic Forensic Stream Ingestion</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
