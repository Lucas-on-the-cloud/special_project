$ErrorActionPreference = 'Stop'

$python = 'C:\sp1\.envs\dfd-hr\python.exe'
$root = 'C:\sp1\WGN'
$env:HF_HOME = 'C:\sp1\.cache\huggingface'
$env:TORCH_HOME = 'C:\sp1\.cache\torch'
$env:PYTHONPYCACHEPREFIX = 'C:\sp1\WGN\.pycache'
$env:HF_HUB_OFFLINE = '1'
$env:PYTHONUNBUFFERED = '1'

$mainConfig = Join-Path $root 'configs\wgn_ffpp_c23_official.yaml'
$groups = @('FF-DF', 'FF-F2F', 'FF-FS', 'FF-NT')

foreach ($group in $groups) {
    $slug = $group.ToLower().Replace('ff-', '')
    $output = Join-Path $root "runs\official_cross_manipulation_$slug"
    $summary = Join-Path $output 'summary.json'
    $evaluation = Join-Path $output 'cross_manipulation.json'

    if ((Test-Path $summary) -and (Test-Path $evaluation)) {
        Write-Output "SKIP COMPLETED CROSS-MANIPULATION $group $(Get-Date -Format o)"
        continue
    }

    Write-Output "START CROSS-MANIPULATION $group $(Get-Date -Format o)"
    & $python (Join-Path $root 'train.py') `
        --config $mainConfig `
        --manipulations $group `
        --output-dir $output
    if ($LASTEXITCODE -ne 0) { throw "Training failed: $group" }

    & $python (Join-Path $root 'evaluate_cross_manipulation.py') `
        --config $mainConfig `
        --checkpoint (Join-Path $output 'best.pt') `
        --output $evaluation
    if ($LASTEXITCODE -ne 0) { throw "Cross-manipulation evaluation failed: $group" }
    Write-Output "DONE CROSS-MANIPULATION $group $(Get-Date -Format o)"
}

Write-Output "ALL OFFICIAL CROSS-MANIPULATION EXPERIMENTS COMPLETE $(Get-Date -Format o)"

