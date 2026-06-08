@echo off
setlocal
cd /d "%~dp0"
call pnpm dev --hostname 0.0.0.0 --port 3000
