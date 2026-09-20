@echo off
title VoxSentinalX Automated Test Runner
cd /d "%~dp0"
echo Running 20 Unit and Integration Tests via Pytest...
python -m pytest tests/ -v
pause
