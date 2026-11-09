param([ValidateSet('install','h3','check','nodes')][string]$Action='install')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
Add-Type -AssemblyName System.Windows.Forms
try {
    $portable='C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
    $saved=Join-Path $root 'local.json'
    if (Test-Path $saved) { $portable=(Get-Content $saved -Raw -Encoding UTF8 | ConvertFrom-Json).portable }
    if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe')) -or -not (Test-Path (Join-Path $portable 'ComfyUI\main.py'))) {
        $dialog=New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description='Chọn THƯ MỤC Portable chứa python_embeded và ComfyUI, không chọn file JSON.'
        $dialog.SelectedPath=$portable
        if ($dialog.ShowDialog() -ne 'OK') { exit 1 }
        $portable=$dialog.SelectedPath
        if ((Split-Path $portable -Leaf) -eq 'ComfyUI') { $portable=Split-Path $portable -Parent }
        if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe'))) {
            $inner=Join-Path $portable 'ComfyUI_windows_portable'
            if (Test-Path (Join-Path $inner 'python_embeded\python.exe')) { $portable=$inner }
        }
    }
    $python=Join-Path $portable 'python_embeded\python.exe'
    if (-not (Test-Path $python)) { throw 'Không thấy python_embeded\python.exe; chọn đúng Portable.' }
    Write-Host ('ComfyUI đích: '+$portable) -ForegroundColor Cyan
    & $python -I -X utf8 -s (Join-Path $PSScriptRoot 'install.py') $Action --portable $portable
    exit $LASTEXITCODE
} catch {
    Write-Host ('LỖI: '+$_.Exception.Message) -ForegroundColor Red
    exit 1
}
