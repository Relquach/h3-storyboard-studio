@echo off
setlocal
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run.ps1" -Action uninstall
if errorlevel 1 echo CHUA HOAN TAT. Xem logs va reports trong thu muc bo go.
pause
