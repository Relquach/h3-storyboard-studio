param([ValidateSet('render','preflight','benchmark','prepare')][string]$Mode = 'preflight')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$cfg = Get-Content (Join-Path $root 'local.json') -Raw | ConvertFrom-Json
$python = Join-Path $cfg.portable 'python_embeded\python.exe'
$projectPath = Join-Path $root 'project.json'
if ($Mode -eq 'prepare') {
    Add-Type -AssemblyName System.Windows.Forms
    $pick = New-Object System.Windows.Forms.OpenFileDialog
    $pick.Filter = 'Project JSON (*.json)|*.json'
    $pick.Title = 'Select project JSON exported by the skill, or examples\project.json'
    $pick.InitialDirectory = Join-Path $root 'examples'
    if ($pick.ShowDialog() -ne 'OK') { exit 1 }
    $project = Get-Content $pick.FileName -Raw -Encoding UTF8 | ConvertFrom-Json
    $pick.Filter = 'Images|*.png;*.jpg;*.jpeg;*.webp'
    $pick.Title = 'Select the WHOLE storyboard image'
    if ($pick.ShowDialog() -ne 'OK') { exit 1 }
    $dest = Join-Path $cfg.comfy 'input\h3studio'
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $tag = [Guid]::NewGuid().ToString('N')
    $name = 'storyboard_' + $tag + [IO.Path]::GetExtension($pick.FileName)
    Copy-Item -LiteralPath $pick.FileName -Destination (Join-Path $dest $name)
    $project.storyboard = 'h3studio/' + $name
    foreach ($character in $project.characters) {
        $pick.Title = 'Select sheet for ' + $character.id + ': ' + $character.name
        if ($pick.ShowDialog() -ne 'OK') { exit 1 }
        $name = 'character_' + [Guid]::NewGuid().ToString('N') + [IO.Path]::GetExtension($pick.FileName)
        Copy-Item -LiteralPath $pick.FileName -Destination (Join-Path $dest $name)
        $character.file = 'h3studio/' + $name
    }
    $project | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $projectPath -Encoding UTF8
    Write-Host 'Project prepared. Run PREFLIGHT.bat, then RENDER.bat.'
    exit 0
}
if (-not (Test-Path $projectPath)) { throw 'Run PREPARE-INPUTS.bat first.' }
$taskArgs = @('-s', (Join-Path $PSScriptRoot 'run.py'), $projectPath)
if ($Mode -eq 'benchmark') { $taskArgs += '--benchmark' }
elseif ($Mode -eq 'preflight') { $taskArgs += '--preflight' }
else { $taskArgs += @('--preset','baseline','--enhance') }
& $python @taskArgs
exit $LASTEXITCODE
