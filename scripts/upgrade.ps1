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
$pick = New-Object System.Windows.Forms.OpenFileDialog
$pick.Filter = 'ComfyUI workflow (*.json)|*.json'
$pick.Title = 'Chon workflow JSON da xuat de giu anh/prompt va nang cap UI (Huy neu muon dung PREFLIGHT)'
$pick.InitialDirectory = Join-Path $portable 'ComfyUI\user\default\workflows'
if ($pick.ShowDialog() -eq 'OK') {
    & $python -s (Join-Path $PSScriptRoot 'upgrade_workflow.py') $pick.FileName
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
Write-Host 'Hoan tat. Khoi dong lai ComfyUI, nhan Ctrl+F5, mo file -VI-v0.2.json moi tao.'
Write-Host 'Khong tai lai model. File workflow goc va model duoc giu nguyen.'
