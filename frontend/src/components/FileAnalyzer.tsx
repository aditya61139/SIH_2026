import React, { useState } from 'react';
import { Upload, FileAudio, Film, CheckCircle2, AlertTriangle, ShieldAlert, FileDown, Loader2, RefreshCw, Layers } from 'lucide-react';
import { FileAnalysisReport } from '../types';

interface FileAnalyzerProps {
  apiBaseUrl: string;
}

export const FileAnalyzer: React.FC<FileAnalyzerProps> = ({ apiBaseUrl }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [report, setReport] = useState<FileAnalysisReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setReport(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${apiBaseUrl}/api/analyze-file`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Failed to analyze file');
      }

      const data: FileAnalysisReport = await res.json();
      setReport(data);
    } catch (err: any) {
      setError(err?.message || 'Error occurred while analyzing the audio file.');
    } finally {
      setLoading(false);
    }
  };

  const isVideoContainer = file?.name.toLowerCase().endsWith('.mp4') ||
    file?.name.toLowerCase().endsWith('.m4a') ||
    file?.name.toLowerCase().endsWith('.mov') ||
    file?.name.toLowerCase().endsWith('.webm');

  const domainShap = report?.domain_shap_contributions ?? {};

  return (
    <div className="space-y-6">
      {/* Upload Box */}
      <div className="rounded-2xl bg-slate-900/80 p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-base font-bold text-white">
            Forensic Audio & MP4 Video File Analyzer
          </h2>
          <span className="rounded bg-cyan-950/80 px-2.5 py-0.5 text-xs font-semibold text-cyan-300 border border-cyan-800">
            MP4 / Audio Supported
          </span>
        </div>
        <p className="text-xs text-slate-400 mb-5">
          Upload phone recordings, voicemail intercepts, video clips, or audio files (MP4, M4A, WAV, MP3, FLAC, OGG, MOV) to demux the voice stream and generate a multi-domain deepfake audit report.
        </p>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-700 bg-slate-950/60 p-8 text-center hover:border-cyan-500/50 hover:bg-slate-950/80 transition-all cursor-pointer"
          onClick={() => document.getElementById('file-upload-input')?.click()}
        >
          <input
            id="file-upload-input"
            type="file"
            accept="audio/*,video/mp4,video/quicktime,video/webm,video/x-matroska,.mp4,.m4a,.wav,.mp3,.flac,.ogg,.aac"
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 mb-3">
            <Upload className="h-6 w-6" />
          </div>
          <p className="text-sm font-semibold text-slate-200">
            {file ? file.name : 'Click to select or drag and drop MP4 / Audio file'}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB • Auto-demux audio track` : 'Supports MP4, M4A, WAV, MP3, FLAC, OGG, MOV up to 100MB'}
          </p>
        </div>

        {file && (
          <div className="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-center space-x-2 text-xs text-slate-300">
              {isVideoContainer ? (
                <Film className="h-4 w-4 text-emerald-400" />
              ) : (
                <FileAudio className="h-4 w-4 text-cyan-400" />
              )}
              <span>
                Selected: <strong>{file.name}</strong>{' '}
                {isVideoContainer && <span className="text-[10px] text-emerald-400 font-mono">(MP4/Video Demuxer Active)</span>}
              </span>
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="flex items-center space-x-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-slate-950 px-5 py-2.5 text-xs font-bold shadow-lg shadow-cyan-500/20 transition-all"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Extracting & Analyzing Forensics...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  <span>Run Multi-Domain Analysis</span>
                </>
              )}
            </button>
          </div>
        )}

        {error && (
          <div className="mt-4 rounded-xl bg-red-500/10 p-3.5 border border-red-500/30 text-xs text-red-300">
            {error}
          </div>
        )}
      </div>

      {/* Forensic Report View */}
      {report && (
        <div className="space-y-6">
          {/* Summary Banner */}
          <div className={`rounded-2xl p-6 border transition-all ${
            report.risk_level === 'CRITICAL'
              ? 'bg-red-950/40 border-red-500/40 glow-red'
              : report.risk_level === 'HIGH'
              ? 'bg-orange-950/40 border-orange-500/40 glow-amber'
              : report.risk_level === 'MODERATE'
              ? 'bg-amber-950/40 border-amber-500/40'
              : 'bg-emerald-950/30 border-emerald-500/30 glow-green'
          }`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Multi-Domain Forensic Result for: {report.filename} ({report.format || 'AUDIO'})
                  </span>
                </div>
                <h3 className="text-2xl font-extrabold text-white mt-1">
                  Verdict: <span className={
                    report.risk_level === 'CRITICAL' ? 'text-red-400' :
                    report.risk_level === 'HIGH' ? 'text-orange-400' :
                    report.risk_level === 'MODERATE' ? 'text-amber-400' : 'text-emerald-400'
                  }>{report.overall_verdict.replace(/_/g, ' ')}</span>
                </h3>
                <p className="text-xs text-slate-300 mt-2 max-w-2xl">
                  {report.recommendation}
                </p>
              </div>

              {/* Score Badges */}
              <div className="flex items-center space-x-4 bg-slate-950/80 p-4 rounded-xl border border-slate-800">
                <div className="text-center">
                  <span className="text-[10px] text-slate-400 block uppercase">Peak Risk</span>
                  <span className="text-2xl font-mono font-bold text-white">
                    {Math.round(report.peak_risk_score * 100)}%
                  </span>
                </div>
                <div className="h-8 w-px bg-slate-800" />
                <div className="text-center">
                  <span className="text-[10px] text-slate-400 block uppercase">Average Risk</span>
                  <span className="text-2xl font-mono font-bold text-cyan-400">
                    {Math.round(report.average_risk_score * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 6-Domain SHAP Contribution Attribution (Chhatriwala et al. 2026 Figure 7) */}
          <div className="rounded-2xl bg-slate-900/80 p-6 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                <h4 className="text-sm font-bold text-white uppercase tracking-wider">
                  SHAP Grouped Feature Stream Importance (Domain Attribution)
                </h4>
              </div>
              <span className="text-[11px] font-mono text-cyan-400">ITEGAM-JETIA 2026 Model</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
              {/* Compression */}
              <div className="rounded-xl bg-slate-950/70 p-3.5 border border-slate-800/80">
                <div className="text-[10px] text-cyan-400 font-bold uppercase truncate">
                  Compression Δk
                </div>
                <div className="mt-1.5 text-xl font-mono font-bold text-white">
                  {Math.round((domainShap.compression ?? 0.28) * 100)}%
                </div>
                <div className="mt-2 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full bg-cyan-400" style={{ width: `${Math.round((domainShap.compression ?? 0.28) * 100)}%` }} />
                </div>
              </div>

              {/* Acoustic */}
              <div className="rounded-xl bg-slate-950/70 p-3.5 border border-slate-800/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase truncate">
                  Acoustic MFCC
                </div>
                <div className="mt-1.5 text-xl font-mono font-bold text-white">
                  {Math.round((domainShap.acoustic ?? 0.22) * 100)}%
                </div>
                <div className="mt-2 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full bg-emerald-400" style={{ width: `${Math.round((domainShap.acoustic ?? 0.22) * 100)}%` }} />
                </div>
              </div>

              {/* Prosody */}
              <div className="rounded-xl bg-slate-950/70 p-3.5 border border-slate-800/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase truncate">
                  Prosody/Jitter
                </div>
                <div className="mt-1.5 text-xl font-mono font-bold text-white">
                  {Math.round((domainShap.prosody ?? 0.20) * 100)}%
                </div>
                <div className="mt-2 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full bg-amber-400" style={{ width: `${Math.round((domainShap.prosody ?? 0.20) * 100)}%` }} />
                </div>
              </div>

              {/* Phase */}
              <div className="rounded-xl bg-slate-950/70 p-3.5 border border-slate-800/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase truncate">
                  Phase Delay
                </div>
                <div className="mt-1.5 text-xl font-mono font-bold text-white">
                  {Math.round((domainShap.phase ?? 0.12) * 100)}%
                </div>
                <div className="mt-2 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full bg-indigo-400" style={{ width: `${Math.round((domainShap.phase ?? 0.12) * 100)}%` }} />
                </div>
              </div>

              {/* Emotional */}
              <div className="rounded-xl bg-slate-950/70 p-3.5 border border-slate-800/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase truncate">
                  Emotional LLD
                </div>
                <div className="mt-1.5 text-xl font-mono font-bold text-white">
                  {Math.round((domainShap.emotional ?? 0.10) * 100)}%
                </div>
                <div className="mt-2 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full bg-purple-400" style={{ width: `${Math.round((domainShap.emotional ?? 0.10) * 100)}%` }} />
                </div>
              </div>

              {/* Spectral */}
              <div className="rounded-xl bg-slate-950/70 p-3.5 border border-slate-800/80">
                <div className="text-[10px] text-slate-400 font-bold uppercase truncate">
                  Spectral Stat
                </div>
                <div className="mt-1.5 text-xl font-mono font-bold text-white">
                  {Math.round((domainShap.statistical_spectral ?? 0.08) * 100)}%
                </div>
                <div className="mt-2 h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                  <div className="h-full bg-rose-400" style={{ width: `${Math.round((domainShap.statistical_spectral ?? 0.08) * 100)}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Timeline Risk Chart */}
          <div className="rounded-2xl bg-slate-900/80 p-6 border border-slate-800">
            <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-wider">
              Temporal Risk Trajectory (2.0s Sliding Windows)
            </h4>
            <div className="h-44 flex items-end space-x-1.5 bg-slate-950 p-4 rounded-xl border border-slate-800/80 overflow-x-auto">
              {report.timeline.map((item, idx) => {
                const heightPercent = Math.max(item.risk_score * 100, 5);
                let barColor = 'bg-emerald-500';
                if (item.risk_level === 'CRITICAL') barColor = 'bg-red-500';
                else if (item.risk_level === 'HIGH') barColor = 'bg-orange-500';
                else if (item.risk_level === 'MODERATE') barColor = 'bg-amber-500';

                return (
                  <div
                    key={idx}
                    className="flex-1 flex flex-col items-center group relative min-w-[24px]"
                  >
                    <div
                      className={`w-full rounded-t transition-all ${barColor} group-hover:brightness-125`}
                      style={{ height: `${heightPercent}%` }}
                    />
                    <span className="text-[9px] font-mono text-slate-500 mt-1">
                      {item.timestamp}
                    </span>

                    {/* Tooltip */}
                    <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col bg-slate-900 text-white text-[10px] p-2 rounded border border-slate-700 shadow-xl z-10 w-44 pointer-events-none">
                      <span className="font-bold">{item.timestamp}</span>
                      <span>Risk: {Math.round(item.risk_score * 100)}% ({item.risk_level})</span>
                      <span className="text-slate-400">{item.diagnostics.length} Anomalies</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Unique Anomalies Breakdown */}
          <div className="rounded-2xl bg-slate-900/80 p-6 border border-slate-800">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider">
                Multi-Domain Forensic Anomalies ({report.unique_anomalies_detected.length})
              </h4>
              <button
                onClick={() => {
                  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
                  const dlAnchor = document.createElement('a');
                  dlAnchor.setAttribute("href", dataStr);
                  dlAnchor.setAttribute("download", `VoxSentinalX_Report_${report.filename}.json`);
                  document.body.appendChild(dlAnchor);
                  dlAnchor.click();
                  dlAnchor.remove();
                }}
                className="flex items-center space-x-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 px-3 py-1.5 text-xs font-semibold text-cyan-400 border border-slate-700"
              >
                <FileDown className="h-4 w-4" />
                <span>Export Report JSON</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {report.unique_anomalies_detected.map((anom, i) => (
                <div key={i} className="rounded-xl bg-slate-950/70 p-4 border border-slate-800">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{anom.metric_name}</span>
                    <span className="text-[10px] font-bold text-red-400 bg-red-500/20 px-2 py-0.5 rounded border border-red-500/30">
                      {anom.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                    {anom.description}
                  </p>
                  <div className="mt-3 flex items-center justify-between text-[10px] font-mono text-slate-400 bg-slate-900/80 p-2 rounded border border-slate-800">
                    <span>Threshold: {anom.threshold}</span>
                    {anom.source_detector && (
                      <span className="text-cyan-400">Layer: {anom.source_detector}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
