"""WebSocket Handler for Bidirectional Real-Time Audio Streaming."""
import json
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.config import settings
from app.audio.stream_buffer import StreamBuffer
from app.engine.fusion_scorer import DetectionEngine
from app.audio.preprocessor import AudioPreprocessor

router = APIRouter()


@router.websocket("/ws/analyze")
async def websocket_analyze_endpoint(websocket: WebSocket):
    """
    Live Audio Streaming Endpoint.
    Receives continuous Int16 PCM chunks via WebSocket, feeds circular buffer,
    executes sliding-window forensic detection, and pushes real-time alerts.
    """
    await websocket.accept()

    buffer = StreamBuffer(
        sample_rate=settings.SAMPLE_RATE,
        window_samples=settings.WINDOW_SAMPLES,
        hop_samples=settings.HOP_SAMPLES,
        capacity_samples=settings.BUFFER_CAPACITY_SAMPLES,
    )
    engine = DetectionEngine()

    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "VoxSentinalX Real-Time Forensic Audio Engine Ready",
            "config": {
                "sample_rate": settings.SAMPLE_RATE,
                "window_duration_sec": settings.WINDOW_DURATION_SEC,
                "hop_duration_sec": settings.HOP_DURATION_SEC,
            },
        })

        while True:
            # Receive either binary audio or JSON control message
            message = await websocket.receive()

            if "bytes" in message and message["bytes"]:
                raw_bytes = message["bytes"]
                window = buffer.add_pcm16_bytes(raw_bytes)

                if window is not None:
                    # Run forensic multi-layer analysis
                    timestamp_sec = buffer.window_count * settings.HOP_DURATION_SEC
                    result = engine.analyze_window(
                        audio_window=window,
                        sample_rate=settings.SAMPLE_RATE,
                        window_index=buffer.window_count,
                        timestamp_sec=timestamp_sec,
                    )
                    result["type"] = "ANALYSIS_UPDATE"
                    await websocket.send_json(result)

            elif "text" in message and message["text"]:
                try:
                    payload = json.loads(message["text"])
                    action = payload.get("action", "")

                    if action == "calibrate":
                        # Calibrate user's voiceprint
                        user_pcm_b64 = payload.get("pcm_data", [])
                        if user_pcm_b64:
                            user_samples = np.array(user_pcm_b64, dtype=np.float32)
                            calib_res = engine.speaker_separator.calibrate(
                                user_samples, settings.SAMPLE_RATE
                            )
                            await websocket.send_json({
                                "type": "CALIBRATION_RESULT",
                                **calib_res,
                            })

                    elif action == "reset":
                        buffer.reset()
                        engine.reset()
                        await websocket.send_json({
                            "type": "RESET_COMPLETE",
                            "message": "Session and buffers reset successfully.",
                        })

                    elif action == "ping":
                        await websocket.send_json({"type": "PONG"})

                except json.JSONDecodeError:
                    pass

    except WebSocketDisconnect:
        # Client disconnected cleanly
        pass
    except Exception as e:
        # Unexpected error handling
        try:
            await websocket.send_json({
                "type": "ERROR",
                "message": f"Stream analysis error: {str(e)}",
            })
        except Exception:
            pass
