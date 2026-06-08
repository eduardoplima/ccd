@echo off
setlocal
cd /d "%~dp0"
uv run arq app.worker.WorkerSettings
