@echo off
cd /d "%~dp0"
start "ITCare AI Frontend" cmd /k "python -m http.server 5500 --bind 127.0.0.1"
timeout /t 2 >nul
start "" http://127.0.0.1:5500/index.html
