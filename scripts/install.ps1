$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$portable = 'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe'))) {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = 'Select ComfyUI Portable root (contains python_embeded and ComfyUI)'
    if ($dialog.ShowDialog() -ne 'OK') { exit 1 }
    $portable = $dialog.SelectedPath
}
$python = Join-Path $portable 'python_embeded\python.exe'
if (-not (Test-Path $python)) { throw 'Embedded Python not found.' }
Write-Host 'Installing pinned community nodes and downloading about 30 GB of model weights.'
Write-Host 'Dependencies are installed into this Portable Python; close ComfyUI first.'
& $python -s (Join-Path $PSScriptRoot 'install.py') --portable $portable
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
