@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run.ps1" -Action check-nodes
set "PATCH_EXIT=%ERRORLEVEL%"
pause
exit /b %PATCH_EXIT%
