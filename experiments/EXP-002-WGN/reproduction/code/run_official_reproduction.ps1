$ErrorActionPreference = 'Stop'

$python = 'C:\sp1\.envs\dfd-hr\python.exe'
$root = 'C:\sp1\WGN'
$env:HF_HOME = 'C:\sp1\.cache\huggingface'
$env:TORCH_HOME = 'C:\sp1\.cache\torch'
$env:PYTHONPYCACHEPREFIX = 'C:\sp1\WGN\.pycache'
$env:HF_HUB_OFFLINE = '1'
$env:PYTHONUNBUFFERED = '1'

function Run-Training($config) {
    Write-Output "START TRAIN $config $(Get-Date -Format o)"
    & $python (Join-Path $root 'train.py') --config (Join-Path $root "configs\$config")
    if ($LASTEXITCODE -ne 0) { throw "Training failed: $config" }
    Write-Output "DONE TRAIN $config $(Get-Date -Format o)"
}

Run-Training 'wgn_ffpp_c23_official.yaml'

$mainCheckpoint = Join-Path $root 'runs\wgn_ffpp_c23_official\best.pt'
$mainConfig = Join-Path $root 'configs\wgn_ffpp_c23_official.yaml'
$crossDatasets = @(
    @('Celeb-DF-v2', 'C:\sp1\data\Celeb-DF-v2.json', 'CelebDFv2_real', 'CelebDFv2_fake', 'cross_celeb_df_v2.json'),
    @('DFDC', 'C:\sp1\data\DFDC.json', 'DFDC_Real', 'DFDC_Fake', 'cross_dfdc.json'),
    @('WildDeepfake', 'C:\sp1\data\WildDeepfake.json', 'WildDeepfake_Real', 'WildDeepfake_Fake', 'cross_wilddeepfake.json')
)
foreach ($item in $crossDatasets) {
    & $python (Join-Path $root 'evaluate_cross_dataset.py') `
        --config $mainConfig `
        --checkpoint $mainCheckpoint `
        --json $item[1] `
        --data-root 'C:\sp1\data' `
        --dataset $item[0] `
        --real-group $item[2] `
        --fake-group $item[3] `
        --split test `
        --output (Join-Path $root "runs\wgn_ffpp_c23_official\$($item[4])")
    if ($LASTEXITCODE -ne 0) { throw "Cross-dataset evaluation failed: $($item[0])" }
}

Run-Training 'wgn_ffpp_c40_official.yaml'
Run-Training 'wgn_faceshifter_c23_official.yaml'
Run-Training 'wgn_faceshifter_c40_official.yaml'

$groups = @('FF-DF', 'FF-F2F', 'FF-FS', 'FF-NT')
foreach ($group in $groups) {
    $slug = $group.ToLower().Replace('ff-', '')
    $output = Join-Path $root "runs\official_cross_manipulation_$slug"
    Write-Output "START CROSS-MANIPULATION $group $(Get-Date -Format o)"
    & $python (Join-Path $root 'train.py') `
        --config $mainConfig `
        --manipulations $group `
        --output-dir $output
    if ($LASTEXITCODE -ne 0) { throw "Cross-manipulation training failed: $group" }
    & $python (Join-Path $root 'evaluate_cross_manipulation.py') `
        --config $mainConfig `
        --checkpoint (Join-Path $output 'best.pt') `
        --output (Join-Path $output 'cross_manipulation.json')
    if ($LASTEXITCODE -ne 0) { throw "Cross-manipulation evaluation failed: $group" }
    Write-Output "DONE CROSS-MANIPULATION $group $(Get-Date -Format o)"
}

Write-Output "ALL OFFICIAL REPRODUCTION EXPERIMENTS COMPLETE $(Get-Date -Format o)"

