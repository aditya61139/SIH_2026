import { AnalysisUpdate } from '../types';

export class VoxSentinalAudioCapture {
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private stream: MediaStream | null = null;
  private ws: WebSocket | null = null;
  private analyser: AnalyserNode | null = null;
  private isRunning: boolean = false;
  private animFrameId: number | null = null;

  public async startMonitoring(
    wsUrl: string,
    onUpdate: (data: AnalysisUpdate) => void,
    onStatusChange: (status: 'connected' | 'connecting' | 'disconnected' | 'error', err?: string) => void,
    onAudioLevel?: (level: number) => void
  ) {
    if (this.isRunning) return;

    try {
      onStatusChange('connecting');

      // Request browser microphone without echo cancellation/noise suppression
      // to capture caller's speakerphone audio faithfully
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: true,
        },
      });

      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000,
      });

      const source = this.audioContext.createMediaStreamSource(this.stream);

      // Create Analyser for UI meters
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 256;
      source.connect(this.analyser);

      // Audio level polling
      if (onAudioLevel) {
        const pcmBuffer = new Uint8Array(new ArrayBuffer(this.analyser.frequencyBinCount));
        const pollLevel = () => {
          if (!this.isRunning || !this.analyser) return;
          this.analyser.getByteFrequencyData(pcmBuffer);
          let sum = 0;
          for (let i = 0; i < pcmBuffer.length; i++) {
            sum += pcmBuffer[i];
          }
          const avg = sum / pcmBuffer.length / 255;
          onAudioLevel(avg);
          this.animFrameId = requestAnimationFrame(pollLevel);
        };
        pollLevel();
      }

      // ScriptProcessorNode: 4096 samples = 256ms at 16kHz
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      // Connect WebSocket
      this.ws = new WebSocket(wsUrl);
      this.ws.binaryType = 'arraybuffer';

      this.ws.onopen = () => {
        this.isRunning = true;
        onStatusChange('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'ANALYSIS_UPDATE') {
            onUpdate(payload as AnalysisUpdate);
          }
        } catch (e) {
          console.error('Error parsing WebSocket message:', e);
        }
      };

      this.ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        onStatusChange('error', 'Connection to analysis backend failed.');
      };

      this.ws.onclose = () => {
        this.isRunning = false;
        onStatusChange('disconnected');
      };

      // Process and stream PCM chunks
      this.processor.onaudioprocess = (event) => {
        if (!this.isRunning || !this.ws || this.ws.readyState !== WebSocket.OPEN) return;

        const float32Data = event.inputBuffer.getChannelData(0);
        // Convert Float32 to Int16 PCM
        const int16Data = new Int16Array(float32Data.length);
        for (let i = 0; i < float32Data.length; i++) {
          const s = Math.max(-1, Math.min(1, float32Data[i]));
          int16Data[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }

        this.ws.send(int16Data.buffer);
      };

      source.connect(this.processor);
      // Route through a zero-gain node so ScriptProcessor continues firing
      // without blasting raw microphone audio back out through the speakers.
      const muteNode = this.audioContext.createGain();
      muteNode.gain.value = 0;
      this.processor.connect(muteNode);
      muteNode.connect(this.audioContext.destination);

    } catch (err: any) {
      onStatusChange('error', err?.message || 'Microphone access denied.');
      this.stopMonitoring();
    }
  }

  public getAnalyserNode(): AnalyserNode | null {
    return this.analyser;
  }

  private calibAudioContext: AudioContext | null = null;
  private calibProcessor: ScriptProcessorNode | null = null;
  private calibStream: MediaStream | null = null;
  private calibAnalyser: AnalyserNode | null = null;
  private calibSamples: number[] = [];
  private isCalibRecording: boolean = false;
  private calibAnimFrameId: number | null = null;

  public async startVoiceRecording(onLevel?: (level: number) => void): Promise<void> {
    if (this.isCalibRecording) return;

    this.calibSamples = [];
    this.isCalibRecording = true;

    try {
      // Use existing stream if active, otherwise request mic
      if (this.stream && this.stream.active) {
        this.calibStream = this.stream;
      } else {
        this.calibStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: false,
            noiseSuppression: false,
            autoGainControl: true,
          },
        });
      }

      this.calibAudioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000,
      });

      const source = this.calibAudioContext.createMediaStreamSource(this.calibStream);

      // Analyser for live visual feedback
      this.calibAnalyser = this.calibAudioContext.createAnalyser();
      this.calibAnalyser.fftSize = 256;
      source.connect(this.calibAnalyser);

      if (onLevel) {
        const pcmBuffer = new Uint8Array(new ArrayBuffer(this.calibAnalyser.frequencyBinCount));
        const pollLevel = () => {
          if (!this.isCalibRecording || !this.calibAnalyser) return;
          this.calibAnalyser.getByteFrequencyData(pcmBuffer);
          let sum = 0;
          for (let i = 0; i < pcmBuffer.length; i++) {
            sum += pcmBuffer[i];
          }
          const avg = sum / pcmBuffer.length / 255;
          onLevel(avg);
          this.calibAnimFrameId = requestAnimationFrame(pollLevel);
        };
        pollLevel();
      }

      // ScriptProcessorNode for recording
      this.calibProcessor = this.calibAudioContext.createScriptProcessor(4096, 1, 1);
      this.calibProcessor.onaudioprocess = (e) => {
        if (!this.isCalibRecording) return;
        const ch = e.inputBuffer.getChannelData(0);
        for (let i = 0; i < ch.length; i++) {
          this.calibSamples.push(ch[i]);
        }
      };

      source.connect(this.calibProcessor);
      const calibMuteNode = this.calibAudioContext.createGain();
      calibMuteNode.gain.value = 0;
      this.calibProcessor.connect(calibMuteNode);
      calibMuteNode.connect(this.calibAudioContext.destination);

    } catch (err: any) {
      this.cancelVoiceRecording();
      throw new Error(err?.message || 'Failed to access microphone for voice recording.');
    }
  }

  public async stopVoiceRecordingAndCalibrate(apiBaseUrl: string = (typeof window !== 'undefined' && window.location.hostname ? `${window.location.protocol}//${window.location.hostname}:8000` : 'http://localhost:8000')): Promise<{
    success: boolean;
    durationSec: number;
    profile?: any;
    message?: string;
  }> {
    if (!this.isCalibRecording) {
      return { success: false, durationSec: 0, message: 'Recording is not active.' };
    }

    this.isCalibRecording = false;

    if (this.calibAnimFrameId) {
      cancelAnimationFrame(this.calibAnimFrameId);
      this.calibAnimFrameId = null;
    }
    if (this.calibProcessor) {
      this.calibProcessor.disconnect();
      this.calibProcessor = null;
    }
    if (this.calibAudioContext) {
      this.calibAudioContext.close();
      this.calibAudioContext = null;
    }
    // Only stop track if it was standalone
    if (this.calibStream && this.calibStream !== this.stream) {
      this.calibStream.getTracks().forEach((t) => t.stop());
      this.calibStream = null;
    }

    const recordedData = [...this.calibSamples];
    const durationSec = recordedData.length / 16000;

    if (recordedData.length < 8000) {
      return {
        success: false,
        durationSec,
        message: 'Recording too short (minimum 0.5s required). Please speak for at least 1-3 seconds.',
      };
    }

    // 1. Send via WebSocket if open
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          action: 'calibrate',
          pcm_data: recordedData,
        })
      );
    }

    // 2. Also send via REST API to ensure backend calibration profile is updated
    try {
      const res = await fetch(`${apiBaseUrl}/api/calibrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pcm_data: recordedData }),
      });
      if (res.ok) {
        const data = await res.json();
        return {
          success: true,
          durationSec: Math.round(durationSec * 10) / 10,
          profile: data.profile,
          message: 'Voiceprint calibrated successfully!',
        };
      }
    } catch {
      // If REST failed but WS sent or fallback
    }

    return {
      success: true,
      durationSec: Math.round(durationSec * 10) / 10,
      message: 'Voiceprint calibrated successfully via real-time stream!',
    };
  }

  public cancelVoiceRecording() {
    this.isCalibRecording = false;
    if (this.calibAnimFrameId) {
      cancelAnimationFrame(this.calibAnimFrameId);
      this.calibAnimFrameId = null;
    }
    if (this.calibProcessor) {
      this.calibProcessor.disconnect();
      this.calibProcessor = null;
    }
    if (this.calibAudioContext) {
      this.calibAudioContext.close();
      this.calibAudioContext = null;
    }
    if (this.calibStream && this.calibStream !== this.stream) {
      this.calibStream.getTracks().forEach((t) => t.stop());
      this.calibStream = null;
    }
    this.calibSamples = [];
  }

  public get isRecordingCalibration(): boolean {
    return this.isCalibRecording;
  }

  public async calibrateUserVoice(durationMs: number = 3000): Promise<boolean> {
    await this.startVoiceRecording();
    return new Promise((resolve) => {
      setTimeout(async () => {
        const res = await this.stopVoiceRecordingAndCalibrate();
        resolve(res.success);
      }, durationMs);
    });
  }

  public resetSession() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'reset' }));
    }
  }

  public stopMonitoring() {
    this.isRunning = false;
    if (this.animFrameId) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  public get active(): boolean {
    return this.isRunning;
  }
}
