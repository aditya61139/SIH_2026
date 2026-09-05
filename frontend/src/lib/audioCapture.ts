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
      this.processor.connect(this.audioContext.destination);

    } catch (err: any) {
      onStatusChange('error', err?.message || 'Microphone access denied.');
      this.stopMonitoring();
    }
  }

  public getAnalyserNode(): AnalyserNode | null {
    return this.analyser;
  }

  public async calibrateUserVoice(durationMs: number = 3000): Promise<boolean> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN || !this.stream) {
      return false;
    }

    return new Promise((resolve) => {
      // Record calibration audio
      const audioCtx = new AudioContext({ sampleRate: 16000 });
      const source = audioCtx.createMediaStreamSource(this.stream!);
      const proc = audioCtx.createScriptProcessor(4096, 1, 1);
      const collectedSamples: number[] = [];

      proc.onaudioprocess = (e) => {
        const ch = e.inputBuffer.getChannelData(0);
        for (let i = 0; i < ch.length; i++) {
          collectedSamples.push(ch[i]);
        }
      };

      source.connect(proc);
      proc.connect(audioCtx.destination);

      setTimeout(() => {
        proc.disconnect();
        source.disconnect();
        audioCtx.close();

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(
            JSON.stringify({
              action: 'calibrate',
              pcm_data: collectedSamples,
            })
          );
          resolve(true);
        } else {
          resolve(false);
        }
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
