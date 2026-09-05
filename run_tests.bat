@echo off
title VoxSentinalX Automated Test Runner
cd /d p:\VoxSentinalX
echo Running 14 Unit and Integration Tests via Pytest...
python -m pytest tests/ -v
pause
