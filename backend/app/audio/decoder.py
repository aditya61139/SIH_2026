"""Audio and Video Container Stream Decoder.
Decodes audio tracks from MP4, M4A, MOV, MKV, WEBM, WAV, MP3, FLAC, OGG, and AAC files
into standardized 16kHz Float32 mono PCM arrays.
"""
import io
import os
import tempfile
import subprocess
import numpy as np
import soundfile as sf
from scipy import signal
from typing import Tuple
from app.core.config import settings


class AudioDecoder:
    """
    Multi-format audio extractor and decoder supporting both raw audio files
    and video containers (MP4, M4A, MOV, WEBM, etc.).
    """

    @classmethod
    def decode_to_16k_mono(cls, content: bytes, filename: str = "") -> Tuple[np.ndarray, float]:
        """
        Decodes arbitrary audio/video file content to 16kHz Float32 mono PCM.
        
        Returns:
            audio_data: np.ndarray (float32 array normalized to [-1.0, 1.0])
            duration_seconds: float
        """
        ext = os.path.splitext(filename.lower())[1] if filename else ""

        # For standard uncompressed audio (WAV, FLAC, OGG), try soundfile first
        if ext in [".wav", ".flac", ".ogg"]:
            try:
                audio_io = io.BytesIO(content)
                data, sr = sf.read(audio_io)
                
                # Convert to mono if multi-channel
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)

                # Resample to 16kHz if needed
                if sr != settings.SAMPLE_RATE:
                    num_target = int(len(data) * (settings.SAMPLE_RATE / sr))
                    data = signal.resample(data, num_target)

                audio_data = data.astype(np.float32)
                duration = len(audio_data) / settings.SAMPLE_RATE
                return audio_data, duration
            except Exception:
                pass  # Fall through to FFmpeg decoder

        # For MP4, M4A, MOV, WEBM, MP3, AAC, or corrupted containers, use FFmpeg
        return cls._decode_via_ffmpeg(content, ext or ".mp4")

    @classmethod
    def _decode_via_ffmpeg(cls, content: bytes, ext: str) -> Tuple[np.ndarray, float]:
        """Uses bundled static FFmpeg binary to extract & resample audio track directly."""
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            raise RuntimeError("imageio-ffmpeg is required to decode MP4/video files.")

        # Write to temporary file for reliable seeking and container demuxing
        suffix = ext if ext.startswith(".") else f".{ext}"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # FFmpeg command: extract audio track, resample to 16kHz, mono, s16le PCM output to pipe
            cmd = [
                ffmpeg_exe,
                "-y",
                "-i", tmp_path,
                "-vn",                 # Disable video stream
                "-acodec", "pcm_s16le", # Convert to 16-bit signed integer PCM
                "-ar", str(settings.SAMPLE_RATE), # 16000 Hz
                "-ac", "1",            # Mono
                "-f", "s16le",         # Raw PCM format
                "-"                    # Pipe to stdout
            ]

            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )

            raw_bytes = process.stdout
            if not raw_bytes:
                raise ValueError("No audio stream found in the uploaded file.")

            # Convert Int16 PCM bytes -> Float32 array
            int16_samples = np.frombuffer(raw_bytes, dtype=np.int16)
            audio_data = int16_samples.astype(np.float32) / 32768.0
            duration = len(audio_data) / settings.SAMPLE_RATE

            return audio_data, duration

        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode("utf-8", errors="ignore")
            raise ValueError(f"FFmpeg failed to extract audio from {ext} file: {err_msg[:200]}")
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
