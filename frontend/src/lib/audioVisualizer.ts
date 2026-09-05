export class CanvasAudioVisualizer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private analyser: AnalyserNode;
  private animId: number | null = null;
  private dataArray: Uint8Array<ArrayBuffer>;
  private freqArray: Uint8Array<ArrayBuffer>;
  private riskColor: string = '#06b6d4'; // default cyan

  constructor(canvas: HTMLCanvasElement, analyser: AnalyserNode) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
    this.analyser = analyser;
    this.analyser.fftSize = 512;
    this.dataArray = new Uint8Array(new ArrayBuffer(this.analyser.fftSize));
    this.freqArray = new Uint8Array(new ArrayBuffer(this.analyser.frequencyBinCount));
  }

  public setRiskLevel(level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL') {
    switch (level) {
      case 'CRITICAL':
        this.riskColor = '#ef4444'; // Red
        break;
      case 'HIGH':
        this.riskColor = '#f97316'; // Orange
        break;
      case 'MODERATE':
        this.riskColor = '#f59e0b'; // Amber
        break;
      default:
        this.riskColor = '#10b981'; // Green
    }
  }

  public start() {
    if (this.animId) return;

    const render = () => {
      this.draw();
      this.animId = requestAnimationFrame(render);
    };
    render();
  }

  public stop() {
    if (this.animId) {
      cancelAnimationFrame(this.animId);
      this.animId = null;
    }
    this.clear();
  }

  private clear() {
    this.ctx.fillStyle = '#0f172a';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  private draw() {
    const width = this.canvas.width;
    const height = this.canvas.height;

    this.analyser.getByteTimeDomainData(this.dataArray);
    this.analyser.getByteFrequencyData(this.freqArray);

    // Dark background with subtle grid
    this.ctx.fillStyle = '#0a0d14';
    this.ctx.fillRect(0, 0, width, height);

    // Draw grid
    this.ctx.strokeStyle = '#1e293b';
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    for (let x = 0; x < width; x += 40) {
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, height);
    }
    for (let y = 0; y < height; y += 30) {
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(width, y);
    }
    this.ctx.stroke();

    // 1. Draw Frequency Spectrum Bars (Translucent in background)
    const barWidth = (width / this.freqArray.length) * 2.5;
    let barX = 0;
    for (let i = 0; i < this.freqArray.length; i++) {
      const barHeight = (this.freqArray[i] / 255) * (height * 0.7);
      this.ctx.fillStyle = `${this.riskColor}22`; // 15% opacity
      this.ctx.fillRect(barX, height - barHeight, barWidth, barHeight);
      barX += barWidth + 1;
    }

    // 2. Draw Live Oscilloscope Waveform Line
    this.ctx.lineWidth = 2.5;
    this.ctx.strokeStyle = this.riskColor;
    this.ctx.shadowBlur = 12;
    this.ctx.shadowColor = this.riskColor;

    this.ctx.beginPath();
    const sliceWidth = width / this.dataArray.length;
    let x = 0;

    for (let i = 0; i < this.dataArray.length; i++) {
      const v = this.dataArray[i] / 128.0;
      const y = (v * height) / 2;

      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
      x += sliceWidth;
    }

    this.ctx.lineTo(width, height / 2);
    this.ctx.stroke();
    this.ctx.shadowBlur = 0; // Reset shadow
  }
}
