@echo off
setlocal
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run.ps1" -Action runtime
if errorlevel 1 echo Chua hoan tat. Xem thong bao ben tren va docs\HUONG_DAN.pdf.
pause
