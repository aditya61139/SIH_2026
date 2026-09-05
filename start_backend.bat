@echo off
title VoxSentinalX Backend Server
cd /d p:\VoxSentinalX\backend
echo Starting VoxSentinalX FastAPI Backend Server...
echo API Docs available at http://localhost:8000/docs
echo WebSocket endpoint at ws://localhost:8000/ws/analyze
python run.py
pause
