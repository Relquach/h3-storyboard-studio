param([ValidateSet('inspect','uninstall')][string]$Action='inspect')
$ErrorActionPreference='Stop'
$utf8=New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding=$utf8
[Console]::OutputEncoding=$utf8
$OutputEncoding=$utf8
$env:PYTHONUTF8='1'
$root=Split-Path $PSScriptRoot -Parent
try {
    $portable='C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
    $saved=Join-Path $root 'local.json'
    if (Test-Path $saved) { $portable=(Get-Content $saved -Raw -Encoding UTF8 | ConvertFrom-Json).portable }
    if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe')) -or -not (Test-Path (Join-Path $portable 'ComfyUI\main.py'))) {
        Add-Type -AssemblyName System.Windows.Forms
        $dialog=New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description='Chon THU MUC Portable chua python_embeded va ComfyUI. Khong chon JSON.'
        if ($dialog.ShowDialog() -ne 'OK') { exit 1 }
        $portable=$dialog.SelectedPath
        if ((Split-Path $portable -Leaf) -eq 'ComfyUI') { $portable=Split-Path $portable -Parent }
        if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe'))) {
            $inner=Join-Path $portable 'ComfyUI_windows_portable'
            if (Test-Path (Join-Path $inner 'python_embeded\python.exe')) { $portable=$inner }
        }
    }
    $python=Join-Path $portable 'python_embeded\python.exe'
    if (-not (Test-Path $python) -or -not (Test-Path (Join-Path $portable 'ComfyUI\main.py'))) { throw 'Khong thay Portable hop le.' }
    @{ portable=$portable } | ConvertTo-Json | Set-Content (Join-Path $root 'local.json') -Encoding UTF8
    Write-Host ('COMFYUI DICH: '+$portable) -ForegroundColor Cyan
    & $python -I -X utf8 -s (Join-Path $PSScriptRoot 'uninstall.py') $Action --portable $portable
    exit $LASTEXITCODE
} catch {
    Write-Host ('LOI: '+$_.Exception.Message) -ForegroundColor Red
    exit 1
}
