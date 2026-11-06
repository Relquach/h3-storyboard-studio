@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1"
if errorlevel 1 echo Installation failed. Read the error above. Existing ComfyUI was not replaced.
pause
