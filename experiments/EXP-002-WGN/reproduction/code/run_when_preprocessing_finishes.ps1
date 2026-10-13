$ErrorActionPreference = 'Stop'

$python = 'C:\sp1\.envs\dfd-hr\python.exe'
$root = 'C:\sp1\WGN'
$manifest = 'C:\sp1\data\FaceForensics++-official.json'
$notBefore = Get-Date '2026-10-13T10:14:18'

Write-Output "WAITING_FOR_PREPROCESSING $(Get-Date -Format o)"
while ($true) {
    $file = Get-Item $manifest -ErrorAction SilentlyContinue
    if ($null -ne $file -and $file.LastWriteTime -ge $notBefore) { break }
    Start-Sleep -Seconds 15
}

Write-Output "VALIDATING_DATASET $(Get-Date -Format o)"
& $python (Join-Path $root 'validate_ffpp_official.py')
if ($LASTEXITCODE -ne 0) { throw 'Official FF++ validation failed' }

Write-Output "STARTING_OFFICIAL_REPRODUCTION $(Get-Date -Format o)"
& (Join-Path $root 'run_official_reproduction.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Official reproduction runner failed' }

Write-Output "PIPELINE_COMPLETE $(Get-Date -Format o)"

