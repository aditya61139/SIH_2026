import React, { useState, useRef } from 'react';
import {
  Upload,
  FileAudio,
  Video,
  AlertTriangle,
  ShieldAlert,
  FileDown,
  Loader2,
  RefreshCw,
  Play,
  Film,
  Globe,
  ShieldCheck,
  CheckCircle2,
  Copy,
  Check,
  Radio,
  Award,
  Volume2,
} from 'lucide-react';
import { FileAnalysisReport } from '../types';
import { DetectionTimeline } from './DetectionTimeline';

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
  const [copiedHash, setCopiedHash] = useState<boolean>(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(true);
    setTimeout(() => setCopiedHash(false), 2000);
  };

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
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-[#94A3B8]">
                    Audit Result for: {report.filename} ({report.duration_seconds}s)
                  </span>
                  {/* Language Profile Pill */}
                  {report.language_profile?.estimated_language && (
                    <span className="flex items-center space-x-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-[#10B981]/15 text-[#10B981] border border-[#10B981]/30">
                      <Globe className="w-3 h-3" />
                      <span>{report.language_profile.estimated_language}</span>
                    </span>
                  )}
                  {/* Replay Pill */}
                  {((report.layer_scores?.replay_attack || 0) >= 0.65 ||
                    (report.replay_profile?.replay_probability || 0) >= 0.65) && (
                    <span className="flex items-center space-x-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-[#8B5CF6]/20 text-[#C4B5FD] border border-[#8B5CF6]/40 animate-pulse">
                      <Volume2 className="w-3 h-3" />
                      <span>PHYSICAL REPLAY ATTACK</span>
                    </span>
                  )}
                </div>

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
                {report.replay_profile && (
                  <>
                    <div className="h-8 w-px bg-[#252830]" />
                    <div className="text-center px-2">
                      <span className="text-[10px] block uppercase font-bold text-[#C4B5FD]">Replay Prob</span>
                      <span className="text-2xl font-mono font-bold text-[#8B5CF6]">
                        {Math.round(report.replay_profile.replay_probability * 100)}%
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Cryptographic Evidence Seal & Compliance Banner */}
          <div className="rounded-3xl p-5 border transition-all bg-[#15171C] border-[#2A2E37] shadow-lg">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start space-x-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      Cryptographic Evidence Certificate
                    </span>
                    <span className="text-[10px] font-mono text-[#10B981] bg-[#10B981]/15 px-2 py-0.5 rounded border border-[#10B981]/30">
                      BSA 2023 / Sec 65B Certified
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-[11px] font-mono text-[#94A3B8]">
                      SHA-256 Digest:
                    </span>
                    <span className="text-[11px] font-mono text-[#E2E8F0] select-all truncate max-w-[240px] sm:max-w-md">
                      {report.sha256_evidence_hash || report.audit_certificate?.media_metadata?.sha256_evidence_hash || 'Computed'}
                    </span>
                    <button
                      onClick={() =>
                        copyToClipboard(
                          report.sha256_evidence_hash ||
                            report.audit_certificate?.media_metadata?.sha256_evidence_hash ||
                            ''
                        )
                      }
                      className="p-1 text-[#94A3B8] hover:text-white transition-colors"
                      title="Copy SHA-256 hash"
                    >
                      {copiedHash ? <Check className="w-3.5 h-3.5 text-[#10B981]" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    const certData = report.audit_certificate || report;
                    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(certData, null, 2));
                    const dlAnchor = document.createElement('a');
                    dlAnchor.setAttribute("href", dataStr);
                    dlAnchor.setAttribute("download", `VoxSentinalX_Forensic_Seal_${report.filename}.json`);
                    document.body.appendChild(dlAnchor);
                    dlAnchor.click();
                    dlAnchor.remove();
                  }}
                  className="flex items-center space-x-1.5 rounded-xl px-4 py-2 text-xs font-semibold border transition-all bg-[#1A1C23] hover:bg-[#10B981]/10 text-[#10B981] border-[#2A2E37] shadow-xs"
                >
                  <Award className="h-4 w-4" />
                  <span>Download Audit Certificate (.json)</span>
                </button>
              </div>
            </div>
          </div>

          {/* Interactive Detection Timeline */}
          <div className="rounded-3xl p-6 sm:p-8 border transition-all bg-[#1A1C23] border-[#2A2E37] shadow-xl">
            <DetectionTimeline
              timeline={report.timeline}
              activeTimestamp={activeTimestamp}
              onSeek={handleSeek}
              durationSeconds={report.duration_seconds}
            />
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
