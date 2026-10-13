# WGN reproduction

This directory contains an independent implementation of **WGN: Wavelet-Guided
Network for Efficient and Generalised Deepfake Detection** reconstructed from
the architecture, equations, and experimental protocol reported in the paper.
It is not an official code release from the paper authors.

## Implemented protocol

- MobileViT-S backbone initialized with ImageNet weights (`timm`)
- Haar wavelet-guided spatial attention (WGSA)
- Adam, learning rate `1e-4`, cosine schedule, batch size `32`
- 25 training epochs, input size `256 x 256`, random seed `1024`
- FaceForensics++ c23/c40 evaluation
- FaceShifter c23/c40 evaluation
- Cross-dataset evaluation on Celeb-DF-v2, DFDC, and WildDeepfake
- Leave-one-manipulation-out evaluation on Deepfakes, Face2Face, FaceSwap,
  and NeuralTextures

The experiment configs preserve the exact paths used on the reproduction
workstation (`C:/sp1`). Change `data.root`, `data.json`, and
`training.output_dir` when running elsewhere.

## Environment

The measured environment was Python 3.10, PyTorch 2.7.1 + CUDA 12.8, and an
NVIDIA RTX 5090 32 GB. Install a CUDA-compatible PyTorch build first, then:

```powershell
python -m pip install -r requirements.txt
```

No administrator access is required when using a virtual environment or conda
environment owned by the current user.

## Data preparation

FaceForensics++ access is governed by its authors' terms. After approval, place
their official `faceforensics_download_v4.py` beside these scripts (a snapshot
used in this run is included) and download from the currently available EU2
server. The helper launches independent compression/manipulation downloads:

```powershell
python download_ffpp_official_parallel.py
python preprocess_ffpp_official_parallel.py
python validate_ffpp_official.py
```

The preprocessing samples 40 frames per real video and 10 frames per fake
video, detects/crops faces with MTCNN, resizes them to 256 x 256, and writes the
JSON manifest expected by the data loader. Official FaceForensics++ train,
validation, and test pairs are stored in `splits/`.

Celeb-DF-v2, DFDC, and WildDeepfake must be acquired separately under their
respective licenses. Their manifests use the same JSON layout as the provided
FaceForensics++ manifest. `prepare_wilddeepfake_json.py` builds the
WildDeepfake manifest from an extracted dataset.

## Run

Run the complete paper-aligned sequence:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_official_reproduction.ps1
```

Or train/evaluate individual experiments:

```powershell
python train.py --config configs/wgn_ffpp_c23_official.yaml
python evaluate_cross_dataset.py `
  --config configs/wgn_ffpp_c23_official.yaml `
  --checkpoint runs/wgn_ffpp_c23_official/best.pt `
  --json C:/path/to/Celeb-DF-v2.json `
  --data-root C:/path/to/data `
  --dataset Celeb-DF-v2 --real-group CelebDFv2_real `
  --fake-group CelebDFv2_fake --split test `
  --output runs/wgn_ffpp_c23_official/cross_celeb_df_v2.json
```

`train.py` selects `best.pt` by validation accuracy and writes per-epoch metrics
to `metrics.jsonl`; final frame- and video-level metrics are stored in
`summary.json`. Dataset files, generated crops, checkpoints, and logs are
deliberately excluded from the repository.

## Reproducibility note

The paper does not publish every low-level implementation detail. Choices that
had to be inferred are documented in the interim report one directory above.
Accordingly, results should be described as a faithful independent
reproduction, not a byte-identical rerun of author code.

