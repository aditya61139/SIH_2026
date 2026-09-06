@echo off
title VoxSentinalX Launcher
echo ================================================================
echo        VoxSentinalX - Real-Time AI Voice Cloning Detection
echo                  SIH Problem Statement #26104
echo ================================================================
echo.
echo [1/2] Starting Backend Server (FastAPI + WebSocket Streamer)...
start "VoxSentinalX Backend (Port 8000)" cmd /k "cd /d ""%~dp0backend"" && python run.py"

echo.
echo [2/2] Starting Frontend UI (React + Web Audio API Visualizer)...
start "VoxSentinalX Frontend (Port 3000)" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

echo.
echo ================================================================
echo  Servers are launching in separate CMD windows!
echo  - Frontend Dashboard : http://localhost:3000
echo  - Backend API Docs   : http://localhost:8000/docs
echo  - WebSocket Stream   : ws://localhost:8000/ws/analyze
echo ================================================================
echo.
pause
