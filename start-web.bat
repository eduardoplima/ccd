@echo off
setlocal
cd /d "%~dp0web"

rem Redis (fila do worker ARQ) via docker compose; exige o Docker Desktop aberto
docker compose up -d redis || echo [aviso] Redis nao subiu - o worker vai falhar ate o Docker Desktop estar rodando.

start "ccd-backend"  cmd /k "%~dp0web\backend\start.bat"
start "ccd-worker"   cmd /k "%~dp0web\backend\start-worker.bat"
start "ccd-frontend" cmd /k "%~dp0web\frontend\start.bat"

echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:3000
