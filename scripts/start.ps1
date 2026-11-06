$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$cfg = Get-Content (Join-Path $root 'local.json') -Raw | ConvertFrom-Json
$python = Join-Path $cfg.portable 'python_embeded\python.exe'
try {
    $stats = Invoke-RestMethod -Uri 'http://127.0.0.1:8188/system_stats' -TimeoutSec 3
    if ($stats.system) { Start-Process 'http://127.0.0.1:8188'; Write-Host 'Using the existing ComfyUI server.'; exit 0 }
} catch {}
# Studio launcher never changes the user's original run_nvidia_gpu.bat.
Start-Process -FilePath $python -WorkingDirectory $cfg.portable -ArgumentList '-s ComfyUI\main.py --windows-standalone-build --lowvram --preview-method none'
Start-Process 'http://127.0.0.1:8188'
Write-Host 'Wait for ComfyUI to load. Use RENDER.bat, PREFLIGHT.bat or BENCHMARK.bat.'
