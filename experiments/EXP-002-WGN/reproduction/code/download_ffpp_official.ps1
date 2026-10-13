$ErrorActionPreference = "Stop"

$python = "C:\sp1\.envs\dfd-hr\python.exe"
$downloader = "C:\sp1\WGN\faceforensics_download_v4.py"
$output = "C:\sp1\data\FaceForensics++-official"
$datasets = @(
    "original",
    "Deepfakes",
    "Face2Face",
    "FaceSwap",
    "NeuralTextures",
    "FaceShifter"
)
$compressions = @("c23", "c40")

New-Item -ItemType Directory -Path $output -Force | Out-Null

foreach ($compression in $compressions) {
    foreach ($dataset in $datasets) {
        Write-Output "START dataset=$dataset compression=$compression timestamp=$(Get-Date -Format o)"
        # The user explicitly confirmed the FaceForensics Terms of Use before
        # this launcher was executed. The empty line answers the official
        # downloader's confirmation prompt for each independent invocation.
        "" | & $python $downloader $output `
            --dataset $dataset `
            --compression $compression `
            --type videos `
            --server EU2
        if ($LASTEXITCODE -ne 0) {
            throw "Download failed for dataset=$dataset compression=$compression"
        }
        Write-Output "DONE dataset=$dataset compression=$compression timestamp=$(Get-Date -Format o)"
    }
}

Write-Output "ALL DOWNLOADS COMPLETE timestamp=$(Get-Date -Format o)"

