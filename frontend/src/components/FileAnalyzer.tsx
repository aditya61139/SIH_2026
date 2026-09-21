import React, { useState, useRef } from 'react';
import { Upload, FileAudio, Video, AlertTriangle, ShieldAlert, FileDown, Loader2, RefreshCw, Play, Film } from 'lucide-react';
import { FileAnalysisReport } from '../types';

interface FileAnalyzerProps {
  apiBaseUrl: string;
}

export const FileAnalyzer: React.FC<FileAnalyzerProps> = ({ apiBaseUrl }) => {
  const [file, setFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isVideo, setIsVideo] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [report, setReport] = useState<FileAnalysisReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTimestamp, setActiveTimestamp] = useState<number | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processSelectedFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const processSelectedFile = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    setReport(null);

    const isVid = selectedFile.type.startsWith('video/') || selectedFile.name.toLowerCase().endsWith('.mp4') || selectedFile.name.toLowerCase().endsWith('.webm');
    setIsVideo(isVid);

    if (isVid) {
      const url = URL.createObjectURL(selectedFile);
      setVideoUrl(url);
    } else {
      setVideoUrl(null);
    }
  };

  const handleSeek = (timestampSec: number) => {
    setActiveTimestamp(timestampSec);
    if (videoRef.current) {
      videoRef.current.currentTime = timestampSec;
      videoRef.current.play().catch(() => {});
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
        throw new Error(errData.detail || 'Failed to analyze media file');
      }

      const data: FileAnalysisReport = await res.json();
      setReport(data);
    } catch (err: any) {
      setError(err?.message || 'Error occurred while analyzing the media file.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Box */}
      <div className="rounded-3xl p-6 sm:p-8 border transition-all bg-[#1A1C23] border-[#2A2E37] shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <h2 className="text-lg font-bold text-white">
              Forensic Audio & MP4 Video Analyzer
            </h2>
            <p className="text-xs mt-1 text-[#94A3B8]">
              Upload phone calls, intercepted voicemails, or <strong>MP4 video recordings</strong> to extract and analyze vocal tract biometrics.
            </p>
          </div>
          <span className="text-xs font-bold px-3 py-1 rounded-xl border self-start sm:self-auto text-[#10B981] bg-[#10B981]/10 border-[#10B981]/30">
            WAV, MP3, MP4, FLAC, OGG, WebM
          </span>
        </div>

        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 text-center transition-all cursor-pointer border-[#2A2E37] bg-[#15171C] hover:border-[#10B981] hover:bg-[#10B981]/5"
          onClick={() => document.getElementById('file-upload-input')?.click()}
        >
          <input
            id="file-upload-input"
            type="file"
            accept="audio/*,video/mp4,video/webm,video/quicktime,.mp4,.mov,.webm,.wav,.mp3,.flac,.ogg,.m4a"
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl border mb-3 shadow-xs bg-[#1A1C23] border-[#2A2E37] text-[#10B981]">
            {isVideo ? <Video className="h-7 w-7" /> : <Upload className="h-7 w-7" />}
          </div>
          <p className="text-sm font-bold text-white">
            {file ? file.name : 'Click to select or drag and drop Audio or MP4 Video'}
          </p>
          <p className="text-xs mt-1.5 text-[#94A3B8]">
            {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB (${isVideo ? 'MP4 Video Container' : 'Audio File'})` : 'Supports MP4, WAV, MP3, FLAC, OGG, WebM up to 100MB'}
          </p>
        </div>

        {file && (
          <div className="mt-5 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-2 text-xs text-white">
              {isVideo ? <Film className="h-4 w-4 text-[#10B981]" /> : <FileAudio className="h-4 w-4 text-[#10B981]" />}
              <span>Selected: <strong>{file.name}</strong></span>
            </div>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full sm:w-auto flex items-center justify-center space-x-2 rounded-xl bg-[#10B981] hover:bg-[#059669] disabled:opacity-50 text-[#0D0E11] px-6 py-2.5 text-xs font-bold shadow-lg shadow-[#10B981]/25 transition-all"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-[#0D0E11]" />
                  <span>Extracting & Analyzing Forensics...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4 text-[#0D0E11]" />
                  <span>Run Forensic Analysis</span>
                </>
              )}
            </button>
          </div>
        )}

        {error && (
          <div className="mt-4 rounded-xl bg-[#DC2626]/15 p-4 border border-[#DC2626]/40 text-xs text-[#DC2626] font-medium">
            {error}
          </div>
        )}
      </div>

      {/* Synchronized MP4 Video Player Preview (if MP4 is uploaded) */}
      {isVideo && videoUrl && (
        <div className="rounded-3xl p-6 border transition-all bg-[#1A1C23] border-[#2A2E37] shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Video className="h-5 w-5 text-[#10B981]" />
              <h3 className="text-sm font-bold uppercase tracking-wider text-white">
                Synchronized MP4 Media Playback
              </h3>
            </div>
            <span className="text-xs text-[#94A3B8] font-mono">
              Click any timeline bar below to seek
            </span>
          </div>

          <div className="relative rounded-2xl overflow-hidden bg-black max-w-2xl mx-auto border border-[#2A2E37] shadow-md">
            <video
              ref={videoRef}
              src={videoUrl}
              controls
              className="w-full max-h-80 object-contain mx-auto"
            />
          </div>
        </div>
      )}

      {/* Forensic Report View */}
      {report && (
        <div className="space-y-6">
          {/* Summary Banner */}
          <div className={`rounded-3xl p-6 sm:p-8 border transition-all ${
            report.risk_level === 'CRITICAL'
              ? 'bg-[#DC2626]/15 border-[#DC2626]/40'
              : report.risk_level === 'HIGH'
              ? 'bg-[#EF4444]/15 border-[#EF4444]/40'
              : report.risk_level === 'MODERATE'
              ? 'bg-[#F59E0B]/15 border-[#F59E0B]/40'
              : 'bg-[#10B981]/15 border-[#10B981]/40'
          }`}>
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#94A3B8]">
                  Audit Result for: {report.filename} ({report.duration_seconds}s)
                </span>
                <h3 className="text-2xl sm:text-3xl font-black mt-1 text-white">
                  Verdict: <span className={
                    report.risk_level === 'CRITICAL' ? 'text-[#DC2626]' :
                    report.risk_level === 'HIGH' ? 'text-[#EF4444]' :
                    report.risk_level === 'MODERATE' ? 'text-[#F59E0B]' : 'text-[#10B981]'
                  }>{report.overall_verdict.replace(/_/g, ' ')}</span>
                </h3>
                <p className="text-xs sm:text-sm mt-2 max-w-2xl leading-relaxed text-[#E2E8F0]">
                  {report.recommendation}
                </p>
              </div>

              {/* Score Badges */}
              <div className="flex items-center space-x-4 p-4 rounded-2xl border bg-[#15171C] border-[#2A2E37] shadow-xl">
                <div className="text-center px-2">
                  <span className="text-[10px] block uppercase font-bold text-[#94A3B8]">Peak Risk</span>
                  <span className="text-2xl font-mono font-bold text-[#EF4444]">
                    {Math.round(report.peak_risk_score * 100)}%
                  </span>
                </div>
                <div className="h-8 w-px bg-[#252830]" />
                <div className="text-center px-2">
                  <span className="text-[10px] block uppercase font-bold text-[#94A3B8]">Average Risk</span>
                  <span className="text-2xl font-mono font-bold text-[#10B981]">
                    {Math.round(report.average_risk_score * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Timeline Risk Chart with Clickable Seeking */}
          <div className="rounded-3xl p-6 sm:p-8 border transition-all bg-[#1A1C23] border-[#2A2E37] shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
              <div>
                <h4 className="text-sm font-bold uppercase tracking-wider text-white">
                  Temporal Risk Trajectory (2.0s Sliding Windows)
                </h4>
                <p className="text-xs mt-0.5 text-[#94A3B8]">
                  Click on any bar to jump the video/audio player to that exact second.
                </p>
              </div>
            </div>

            <div className="h-48 flex items-end space-x-1.5 p-4 rounded-2xl border overflow-x-auto bg-[#15171C] border-[#252830]">
              {report.timeline.map((item, idx) => {
                const heightPercent = Math.max(item.risk_score * 100, 6);
                let barColor = 'bg-[#10B981] hover:bg-[#10B981]/80';
                if (item.risk_level === 'CRITICAL') barColor = 'bg-[#DC2626] hover:bg-[#DC2626]/80';
                else if (item.risk_level === 'HIGH') barColor = 'bg-[#EF4444] hover:bg-[#EF4444]/80';
                else if (item.risk_level === 'MODERATE') barColor = 'bg-[#F59E0B] hover:bg-[#F59E0B]/80';

                const timestampSec = idx * 1.0;
                const isSelected = activeTimestamp === timestampSec;

                return (
                  <button
                    key={idx}
                    onClick={() => handleSeek(timestampSec)}
                    className="flex-1 flex flex-col items-center group relative min-w-[28px] focus:outline-none"
                    title={`Timestamp: ${item.timestamp} | Risk: ${Math.round(item.risk_score * 100)}%`}
                  >
                    <div
                      className={`w-full rounded-t transition-all cursor-pointer ${barColor} ${
                        isSelected ? 'ring-2 ring-[#10B981] brightness-125' : ''
                      }`}
                      style={{ height: `${heightPercent}%` }}
                    />
                    <span className={`text-[9px] font-mono mt-1 ${isSelected ? 'text-[#10B981] font-bold' : 'text-[#64748B]'}`}>
                      {item.timestamp}
                    </span>

                    {/* Hover Tooltip */}
                    <div className="absolute bottom-full mb-2 hidden group-hover:flex flex-col bg-[#0D0E11] text-white text-[10px] p-2 rounded-lg border border-[#2A2E37] shadow-2xl z-20 w-36 pointer-events-none">
                      <span className="font-bold text-[#10B981]">{item.timestamp}</span>
                      <span>Risk: {Math.round(item.risk_score * 100)}% ({item.risk_level})</span>
                      <span className="text-[#94A3B8]">{item.diagnostics.length} Anomalies</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Unique Anomalies Breakdown */}
          <div className="rounded-3xl p-6 sm:p-8 border transition-all bg-[#1A1C23] border-[#2A2E37] shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-bold uppercase tracking-wider text-white">
                Forensic Anomaly Breakdown ({report.unique_anomalies_detected.length})
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
                className="flex items-center space-x-1.5 rounded-xl px-4 py-2 text-xs font-semibold border transition-all bg-[#15171C] hover:bg-[#10B981]/10 text-[#10B981] border-[#2A2E37]"
              >
                <FileDown className="h-4 w-4" />
                <span>Export Report JSON</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {report.unique_anomalies_detected.map((anom, i) => (
                <div key={i} className="rounded-2xl p-4 border bg-[#15171C] border-[#2A2E37]">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">{anom.metric_name}</span>
                    <span className="text-[10px] font-bold text-[#EF4444] bg-[#EF4444]/15 px-2 py-0.5 rounded border border-[#EF4444]/30">
                      {anom.severity}
                    </span>
                  </div>
                  <p className="text-xs mt-2 leading-relaxed text-[#94A3B8]">
                    {anom.description}
                  </p>
                  <div className="mt-3 text-[10px] font-mono p-2 rounded-lg border text-[#E2E8F0] bg-[#1A1C23] border-[#252830]">
                    Threshold: {anom.threshold}
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
