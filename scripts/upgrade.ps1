$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$portable = 'C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
$local = Join-Path $root 'local.json'
if (Test-Path $local) { $portable = (Get-Content $local -Raw | ConvertFrom-Json).portable }
Add-Type -AssemblyName System.Windows.Forms
if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe'))) {
    $folder = New-Object System.Windows.Forms.FolderBrowserDialog
    $folder.Description = 'Chon thu muc ComfyUI Portable (chua python_embeded va ComfyUI)'
    if ($folder.ShowDialog() -ne 'OK') { exit 1 }
    $portable = $folder.SelectedPath
}
$python = Join-Path $portable 'python_embeded\python.exe'
& $python -s (Join-Path $PSScriptRoot 'repair.py') --portable $portable
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$source = Join-Path $root 'workflows\lan-15s-vi.json'
$destinationFolder = Join-Path $portable 'ComfyUI\user\default\workflows'
New-Item -ItemType Directory -Force -Path $destinationFolder | Out-Null
$destination = Join-Path $destinationFolder 'H3_Storyboard_VI_v0.3.json'
if (Test-Path $destination) {
    $backupFolder = Join-Path $portable 'ComfyUI\user\h3studio_backups'
    New-Item -ItemType Directory -Force -Path $backupFolder | Out-Null
    Copy-Item -LiteralPath $destination -Destination (Join-Path $backupFolder ('workflow-' + [Guid]::NewGuid().ToString('N') + '.json'))
}
Copy-Item -LiteralPath $source -Destination $destination -Force
Write-Host ('Workflow moi: ' + $destination)
Write-Host 'Hoan tat. Dong han va mo lai ComfyUI, Ctrl+F5, mo H3_Storyboard_VI_v0.3.json trong danh sach workflow.'
Write-Host 'Khong tai lai model. File workflow goc va model duoc giu nguyen.'
