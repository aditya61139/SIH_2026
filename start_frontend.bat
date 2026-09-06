@echo off
title VoxSentinalX Frontend Server
cd /d "%~dp0frontend"
echo Starting VoxSentinalX Frontend Dashboard...
echo Open http://localhost:3000 in your browser
npm run dev
pause
