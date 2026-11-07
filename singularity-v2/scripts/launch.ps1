param([ValidateSet('Install','Start','Prepare','Check')][string]$Action='Install', [string]$Example='Lan15')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Add-Type -AssemblyName System.Windows.Forms
function Pick-File([string]$title,[string]$filter) {
    $d = New-Object System.Windows.Forms.OpenFileDialog
    $d.Title=$title; $d.Filter=$filter
    if ($d.ShowDialog() -ne 'OK') { throw 'Đã hủy chọn file.' }
    return $d.FileName
}
$local = Join-Path $root 'local.json'
try {
    if ($Action -eq 'Install') {
        $portable='C:\Ai\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable'
        if (Test-Path $local) { $portable=(Get-Content $local -Raw -Encoding UTF8 | ConvertFrom-Json).portable }
        if (-not (Test-Path (Join-Path $portable 'python_embeded\python.exe'))) {
            $d=New-Object System.Windows.Forms.FolderBrowserDialog
            $d.Description='Chọn thư mục ComfyUI_windows_portable, chứa python_embeded và ComfyUI'
            if ($d.ShowDialog() -ne 'OK') { throw 'Đã hủy cài.' }; $portable=$d.SelectedPath
        }
        & (Join-Path $portable 'python_embeded\python.exe') -X utf8 -s (Join-Path $PSScriptRoot 'setup_studio.py') install --portable $portable
        if ($LASTEXITCODE -ne 0) { throw 'Cài chưa hoàn tất. Xem lỗi ở trên; chạy lại INSTALL.bat để tiếp tục tải.' }
        exit 0
    }
    if (-not (Test-Path $local)) { throw 'Chạy INSTALL.bat trước.' }
    $conf=Get-Content $local -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Action -eq 'Start') {
        $running=$false
        try { $null=Invoke-WebRequest ($conf.url+'/system_stats') -UseBasicParsing -TimeoutSec 2; $running=$true } catch {}
        if ($running) { Start-Process $conf.url; exit 0 }
        Set-Location $conf.comfy
        & $conf.python -X utf8 -s main.py --windows-standalone-build --use-pytorch-cross-attention --preview-method none --port 8189
        exit $LASTEXITCODE
    }
    if ($Action -eq 'Check') {
        & $conf.python -X utf8 -s (Join-Path $PSScriptRoot 'setup_studio.py') preflight
        exit $LASTEXITCODE
    }
    $choice=[System.Windows.Forms.DialogResult]::Yes
    if ($Example -ne 'Test5') { $choice=[System.Windows.Forms.MessageBox]::Show('Dùng ví dụ Lan 15 giây? Yes = Lan; No = chọn project JSON do skill xuất.','Chuẩn bị storyboard',[System.Windows.Forms.MessageBoxButtons]::YesNoCancel) }
    if ($choice -eq 'Cancel') { exit 1 }
    $projectPath=Join-Path $root 'examples\lan-15s.project.json'
    if ($Example -eq 'Test5') { $projectPath=Join-Path $root 'examples\kiem-tra-5s.project.json' }
    if ($choice -eq 'No') { $projectPath=Pick-File 'Chọn project JSON do skill xuất' 'Project JSON (*.json)|*.json' }
    $project=Get-Content $projectPath -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($asset in $project.assets) {
        if ($asset.enabled -eq $false) { continue }
        if (-not $asset.file -or -not (Test-Path -LiteralPath $asset.file)) {
            $asset.file=Pick-File ('Chọn ảnh cho '+$asset.id+' — '+$asset.name) 'Ảnh (*.png;*.jpg;*.jpeg;*.webp)|*.png;*.jpg;*.jpeg;*.webp'
        }
    }
    $prepared=Join-Path $root 'prepared.project.json'
    $project | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $prepared -Encoding UTF8
    & $conf.python -X utf8 -s (Join-Path $PSScriptRoot 'setup_studio.py') prepare --project $prepared
    if ($LASTEXITCODE -ne 0) { throw 'Chuẩn bị chưa hoàn tất; xem lỗi ở trên.' }
    Write-Host 'Mở workflow READY-... vừa tạo trong danh sách workflow ComfyUI. File ảnh đã được chép và prompt đã khớp dây.'
} catch {
    Write-Host ('LỖI: '+$_.Exception.Message) -ForegroundColor Red
    exit 1
}
