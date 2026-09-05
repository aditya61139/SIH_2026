@echo off
title VoxSentinalX Automated Test Runner
cd /d p:\VoxSentinalX
echo Running 23 Unit, Integration, and Multi-Domain Forensic Tests via Pytest...
python -m pytest tests/ -v
pause

