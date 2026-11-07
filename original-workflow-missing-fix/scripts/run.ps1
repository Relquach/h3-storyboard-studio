param([ValidateSet('install','nodes','check','check-nodes')][string]$Action='install')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
Add-Type -AssemblyName System.Windows.Forms
try {
    $portable='C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
    $saved=Join-Path $root 'local.json'
    $mustChoose=$false
    if (Test-Path $saved) { $portable=(Get-Content $saved -Raw -Encoding UTF8 | ConvertFrom-Json).portable }
    else {
        $active=@()
        try {
            $processes=Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'"
            foreach ($process in $processes) {
                if ($process.CommandLine -notmatch 'main\.py' -or -not $process.ExecutablePath) { continue }
                $candidate=Split-Path (Split-Path $process.ExecutablePath -Parent) -Parent
                if ((Test-Path (Join-Path $candidate 'python_embeded\python.exe')) -and (Test-Path (Join-Path $candidate 'ComfyUI\main.py'))) { $active += $candidate }
            }
        } catch { $active=@() }
        $active=@($active | Select-Object -Unique)
        if ($active.Count -eq 1) { $portable=$active[0] }
        if ($active.Count -gt 1) { $mustChoose=$true }
    }
    if ($mustChoose -or -not (Test-Path (Join-Path $portable 'python_embeded\python.exe')) -or -not (Test-Path (Join-Path $portable 'ComfyUI\main.py'))) {
        $dialog=New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description='Chọn thư mục Portable của ComfyUI bạn dùng (chứa python_embeded và ComfyUI). Chọn thư mục, không chọn JSON.'
        $dialog.SelectedPath=$portable
        if ($dialog.ShowDialog() -ne 'OK') { exit 1 };$portable=$dialog.SelectedPath
        if ((Split-Path $portable -Leaf) -eq 'ComfyUI') { $portable=Split-Path $portable -Parent }
        if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe'))) {
            $inner=Join-Path $portable 'ComfyUI_windows_portable'
            if (Test-Path (Join-Path $inner 'python_embeded\python.exe')) { $portable=$inner }
        }
    }
    Write-Host ('Đích cài: '+$portable) -ForegroundColor Cyan
    & (Join-Path $portable 'python_embeded\python.exe') -I -X utf8 -s (Join-Path $PSScriptRoot 'install_missing.py') $Action --portable $portable
    exit $LASTEXITCODE
} catch {
    Write-Host ('LỖI: '+$_.Exception.Message) -ForegroundColor Red
    exit 1
}
