@echo off
setlocal
cd /d "%~dp0"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
