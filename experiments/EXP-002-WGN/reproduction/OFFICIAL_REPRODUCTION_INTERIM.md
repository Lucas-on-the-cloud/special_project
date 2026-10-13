# WGN Official-Data Reproduction: Interim Report

**Date:** 13 October 2026  
**Paper:** *WGN: Wavelet-Guided Network for Efficient and Generalised Deepfake Detection* (CVPRW 2026)  
**Status:** Main FaceForensics++ c23/c40, cross-dataset evaluation, and FaceShifter c23/c40 are complete; cross-manipulation experiments are still running.

## Reproduction scope and caveat

The authors' official WGN source code and pretrained checkpoint were not publicly available when this reproduction was started. The current implementation is therefore reconstructed from the paper, not claimed to be an exact execution of author-released code. The architecture preserves the reported core design: a pretrained MobileViT-S backbone, Haar-wavelet high-frequency guidance, gated feature fusion, and binary classification.

## Setup used

- GPU: NVIDIA GeForce RTX 5090, 32 GB VRAM
- Environment: local Conda environment on Windows; no administrator-level system changes
- Backbone: `mobilevit_s.cvnets_in1k`, pretrained weights
- Model size: 5,758,793 trainable parameters
- Input: MTCNN face crops resized to 256 x 256
- Official FaceForensics++ split: 720 train / 140 validation / 140 test videos
- Sampling: 40 frames per real video and 10 frames per fake video
- Training: 25 epochs, batch size 32, Adam, learning rate 1e-4, cosine schedule, FP32, seed 1024

## Data preparation completed

- Downloaded 12,000 official FaceForensics++ MP4 files: c23 and c40, each containing Original, Deepfakes, Face2Face, FaceSwap, NeuralTextures, and FaceShifter.
- Generated 180,000 face crops at 256 x 256.
- All 12 preprocessing jobs completed with zero failed jobs and zero center-crop fallbacks.
- MTCNN missed the face on 18 of 180,000 sampled frames (0.01%); those frames reused the nearest valid face box from the same video.
- The final manifest was validated for group, compression, split, video count, frame count, file existence, and sampled image integrity.

## Completed main results

Paper values and our values below are frame-level test metrics.

<table>
  <tr>
    <th width="58%">Original paper - Table 1</th>
    <th width="42%">Our completed reproduction</th>
  </tr>
  <tr>
    <td><img src="assets/wgn-paper-table1-05.png" alt="Original WGN paper Table 1"></td>
    <td valign="top">
      <b>FF++ c23 test</b><br>
      ACC: 94.12% (paper: 95.32%)<br>
      AUC: 98.44% (paper: 98.90%)<br><br>
      <b>FF++ c40 test</b><br>
      ACC: 78.80% (paper: 80.20%)<br>
      AUC: 87.09% (paper: 89.00%)<br><br>
      <b>FaceShifter c23</b><br>
      ACC: 98.24% (paper: 98.00%)<br>
      AUC: 98.88% (paper: 99.92%)<br><br>
      <b>FaceShifter c40</b><br>
      ACC: 93.87% (paper: 94.99%)<br>
      AUC: 97.20% (paper: 98.66%)
    </td>
  </tr>
</table>

| Experiment | Metric | Paper | Ours | Difference |
|---|---:|---:|---:|---:|
| FF++ c23 | ACC | 95.32% | 94.12% | -1.20 pp |
| FF++ c23 | AUC | 98.90% | 98.44% | -0.46 pp |
| FF++ c40 | ACC | 80.20% | 78.80% | -1.40 pp |
| FF++ c40 | AUC | 89.00% | 87.09% | -1.91 pp |
| FaceShifter c23 | ACC | 98.00% | 98.24% | +0.24 pp |
| FaceShifter c23 | AUC | 99.92% | 98.88% | -1.04 pp |
| FaceShifter c40 | ACC | 94.99% | 93.87% | -1.12 pp |
| FaceShifter c40 | AUC | 98.66% | 97.20% | -1.46 pp |

Additional video-level results:

| Experiment | Video ACC | Video AUC |
|---|---:|---:|
| FF++ c23 | 97.00% | 99.51% |
| FF++ c40 | 89.86% | 93.52% |
| FaceShifter c23 | 97.50% | 99.66% |
| FaceShifter c40 | 93.21% | 99.29% |

The c23 run selected epoch 13 (zero-based checkpoint epoch 12) by validation accuracy and took approximately 41 minutes. The c40 run selected epoch 19 (zero-based checkpoint epoch 18) and took approximately 40 minutes.

## Completed cross-dataset evaluation

All evaluations use the best FF++ c23 checkpoint without target-dataset fine-tuning. Both frame- and video-aggregated AUC are reported because the exact aggregation used for the paper table is not fully specified.

<table>
  <tr>
    <th width="58%">Original paper - Table 2</th>
    <th width="42%">Our completed reproduction</th>
  </tr>
  <tr>
    <td><img src="assets/wgn-paper-table2-05.png" alt="Original WGN paper Table 2"></td>
    <td valign="top">
      <b>Celeb-DF-v2</b><br>
      Frame AUC: 65.03%<br>
      Video AUC: 69.70%<br>
      Paper: 77.62%<br><br>
      <b>DFDC</b><br>
      Frame AUC: 69.54%<br>
      Video AUC: 71.00%<br>
      Paper: 70.41%<br><br>
      <b>WildDeepfake</b><br>
      Frame AUC: 70.35%<br>
      Video AUC: 75.35%<br>
      Paper: 68.65%
    </td>
  </tr>
</table>

| Target dataset | Frames | Videos | Frame AUC | Video AUC | Paper AUC |
|---|---:|---:|---:|---:|---:|
| Celeb-DF-v2 | 16,420 | 518 | 65.03% | 69.70% | 77.62% |
| DFDC | 132,116 | 4,704 | 69.54% | 71.00% | 70.41% |
| WildDeepfake | 165,662 | 806 | 70.35% | 75.35% | 68.65% |

## FaceShifter results

Final test metrics from the best validation-accuracy checkpoints are:

| Compression | Best epoch | Frame ACC | Frame AUC | Video ACC | Video AUC |
|---|---:|---:|---:|---:|---:|
| c23 | 12 | 98.24% | 98.88% | 97.50% | 99.66% |
| c40 | 16 | 93.87% | 97.20% | 93.21% | 99.29% |

## Work implemented

- Official FaceForensics++ EU2 parallel downloader and integrity checks
- Official split acquisition and validation
- Resumable parallel MTCNN preprocessing for c23 and c40
- Sequential video decoding optimization to avoid expensive random seeks
- DeepfakeBench-style manifest generation with configurable compression
- WGN training and evaluation code for main, FaceShifter, cross-dataset, and cross-manipulation protocols
- Automatic validation and end-to-end experiment runner
- Separate JSON summaries and metric histories for each experiment

## Remaining work

1. Complete four independent cross-manipulation training/evaluation runs.
2. Add final comparison tables, runtimes, checkpoints, and analysis of remaining gaps to the paper.


