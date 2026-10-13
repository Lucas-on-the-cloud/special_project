$ErrorActionPreference = 'Stop'

$python = 'C:\sp1\.envs\dfd-hr\python.exe'
$root = 'C:\sp1\WGN'
$env:HF_HOME = 'C:\sp1\.cache\huggingface'
$env:TORCH_HOME = 'C:\sp1\.cache\torch'
$env:PYTHONPYCACHEPREFIX = 'C:\sp1\WGN\.pycache'
$env:HF_HUB_OFFLINE = '1'
$env:PYTHONUNBUFFERED = '1'

$groups = @('FF-DF', 'FF-F2F', 'FF-FS', 'FF-NT')
foreach ($group in $groups) {
    $slug = $group.ToLower().Replace('ff-', '')
    $output = Join-Path $root "runs\cross_manipulation_$slug"
    Write-Output "START $group $(Get-Date -Format o)"
    & $python (Join-Path $root 'train.py') --manipulations $group --output-dir $output
    if ($LASTEXITCODE -ne 0) { throw "Training failed for $group" }
    & $python (Join-Path $root 'evaluate_cross_manipulation.py') `
        --checkpoint (Join-Path $output 'best.pt') `
        --output (Join-Path $output 'cross_manipulation.json')
    if ($LASTEXITCODE -ne 0) { throw "Evaluation failed for $group" }
    Write-Output "DONE $group $(Get-Date -Format o)"
}

