# WGN Improvement Plan

**Project:** Generalizable Deepfake Detection  
**Baseline:** WGN independent reproduction  
**Repository:** Lucas-on-the-cloud/special_project  
**Planning date:** 18 October 2026  
**Current priority:** Improve WGN first; DFD-HR is deferred.

## 1. Baseline that must remain frozen

The current WGN reproduction is already complete and must not be overwritten.

| Item | Frozen setting |
|---|---|
| Backbone | MobileViT-S, ImageNet-pretrained |
| Input | MTCNN face crop, 256 x 256 |
| Wavelet module | Haar-wavelet WGSA |
| Dataset | FaceForensics++ |
| Main training split | FF++ c23 |
| Epochs | 25 |
| Batch size | 32 on RTX 5090; reduce to 16 only if VRAM requires it |
| Optimizer | Adam |
| Learning rate | 1e-4 |
| Scheduler | Cosine annealing |
| Seed | 1024 |
| Main metrics | Frame AUC, video AUC, accuracy |
| Generalization tests | FF++ c40, FaceShifter, Celeb-DF v2, DFDC, WildDeepfake, cross-manipulation |

The baseline result is documented in:

- experiments/EXP-002-WGN/reproduction/CURRENT-REPRODUCTION-STATUS.md
- experiments/EXP-002-WGN/reproduction/code/README.md

The baseline must be rerun only as a control when an improvement is trained under a new environment. Do not tune the improvement using the test set.

## Dataset source decision for this phase

- **Training/control:** keep the approved FaceForensics++ c23 pipeline and the existing c40 control unchanged.
- **External evaluation:** use Celeb-DF v2 directly from the authors' MP4 archive with the official 518-video test list and the WGN MTCNN crop pipeline. Retain the approved external packages for DFDC and WildDeepfake.
- **No target fine-tuning:** these external datasets remain locked evaluation sets.
- **No repeated raw preprocessing:** do not run full face detection/cropping on the rented GPU unless the processed archive fails validation.
- **Required preflight:** record archive checksums, inspect sample paths and labels, verify video IDs/split names, require exactly 178 real and 340 fake Celeb-DF test videos, and pass a two-video full-decode/CUDA-forward smoke test before full preprocessing.

## 2. Research problem

The baseline is strong on FF++ c23 but has a clear generalization gap:

- Celeb-DF video AUC: 69.70% (evaluated using the approved external-data protocol)
- DFDC video AUC: 71.00% (evaluated using the approved external-data protocol)
- WildDeepfake video AUC: 75.35% (evaluated using the approved external-data protocol)
- FF++ c40 AUC: 87.09%

The improvement question for this phase is:

> Can complementary gradient cues, difficulty-aware training, or lightweight temporal consistency improve WGN generalization without replacing its wavelet-guided architecture or adding excessive inference cost?

This week we will test the three methods independently. We will not combine them yet.

## 3. Candidate method A — Gradient-aware multi-domain fusion

### Supporting 2026 paper

[A Multi-Domain Feature Fusion Framework for Generalizable Deepfake Detection Across Different Generators (SGFF-Net), 2026](https://arxiv.org/abs/2606.14230)

The paper combines spatial, gradient, and DWT-frequency representations. This is a close match for WGN because WGN already contains spatial features and Haar-wavelet guidance.

### Adaptation for WGN

We will not copy the whole SGFF-Net architecture. We will add only a lightweight gradient branch:

~~~text
MobileViT features       F_spatial
WGSA output              F_wavelet_guided
Sobel/Laplacian branch   F_gradient
             |
      3-way gated fusion
             |
         classifier
~~~

Recommended implementation:

1. Compute a gradient magnitude map from the backbone feature map using fixed Sobel filters.
2. Project the gradient map with a trainable 1x1 convolution.
3. Concatenate F_spatial, F_wavelet_guided, and F_gradient.
4. Use a 1x1 fusion layer and retain the existing binary classifier.
5. Keep the BCE loss unchanged for this first experiment.

This avoids duplicating WGN's wavelet branch and isolates the contribution of gradient information.

### Experiment record

- Variant: EXP-003 / gradient fusion
- Config: configs/wgn_gradient_fusion.yaml
- Output: runs/wgn_gradient_fusion/
- Primary hypothesis: improve Celeb-DF and FF++ c40 AUC.
- Inference cost: expected to be only slightly higher than baseline.

### Required ablation

| Variant | Spatial | WGSA | Gradient | Purpose |
|---|---:|---:|---:|---|
| A0 | yes | yes | no | Frozen WGN baseline |
| A1 | yes | yes | yes | Proposed gradient fusion |

## 4. Candidate method B — Difficulty-aware curriculum learning

### Supporting 2026 paper

[Efficient Domain-Incremental Deepfake Detection via Difficulty-Aware Curriculum Learning, CVPRW 2026](https://openaccess.thecvf.com/content/CVPR2026W/AIMS/html/Park_Efficient_Domain-Incremental_Deepfake_Detection_via_Difficulty-Aware_Curriculum_Learning_CVPRW_2026_paper.html)

The paper studies domain-incremental deepfake detection with difficulty-aware curriculum learning. This direction is attractive because it changes the training schedule, not the inference architecture.

### Adaptation for WGN

We will estimate difficulty only on the training split:

1. Run the frozen baseline checkpoint over the FF++ c23 training frames.
2. Compute per-sample binary cross-entropy loss.
3. Sort samples by loss.
4. Train with an increasing fraction of the sorted data:

~~~text
Epochs 1-8:    easiest 50%
Epochs 9-16:   easiest 75%
Epochs 17-25:  100% of the training samples
~~~

The validation and test sets remain unchanged. The difficulty ranking must never use validation or test labels.

### Experiment record

- Variant: EXP-003 / curriculum
- Config: configs/wgn_curriculum.yaml
- Output: runs/wgn_curriculum/
- Primary hypothesis: improve cross-manipulation and cross-dataset robustness.
- Inference cost: unchanged from baseline.

### Required ablation

| Variant | Training order | Purpose |
|---|---|---|
| B0 | Random shuffle | Baseline control |
| B1 | Easy-to-hard curriculum | Test curriculum effect |

If the baseline checkpoint is unavailable on the rented machine, use a deterministic training-only difficulty proxy and clearly mark that deviation in the experiment log.

## 5. Candidate method C — Lightweight temporal consistency

### Supporting 2026 paper

[Deepfake Detection in Social Media: A Temporal Artifact Analysis Using 3D Convolutional Neural Networks, 2026](https://arxiv.org/abs/2605.17573)

The paper uses video clips and a temporal-consistency regularizer. We will adapt only the regularization idea; we will not replace MobileViT with a 3D CNN.

### Adaptation for WGN

The data loader already stores the source video identifier for each frame. During training:

1. Sample two different frames from the same video.
2. Run both frames through the same WGN model.
3. Apply normal BCE loss to both predictions.
4. Add a consistency term between the two predicted probabilities.

~~~text
L_total = BCE(frame_t) + BCE(frame_t+1)
          + lambda_temporal * MSE(p_t, p_t+1)
~~~

Initial value: lambda_temporal = 0.10.

Inference remains frame-level, so this method does not require two frames at deployment. The temporal pair is used only as a training regularizer.

### Experiment record

- Variant: EXP-003 / temporal consistency
- Config: configs/wgn_temporal_consistency.yaml
- Output: runs/wgn_temporal_consistency/
- Primary hypothesis: improve video-level AUC, especially on DFDC and WildDeepfake.
- Inference cost: unchanged; training cost will increase because two frames are processed.

### Required ablation

| Variant | BCE | Temporal consistency | Purpose |
|---|---:|---:|---|
| C0 | yes | no | Frame-level WGN |
| C1 | yes | yes | Proposed temporal regularization |

## 6. Common experiment protocol

Every candidate must use the same protocol:

~~~text
Train:       FaceForensics++ c23
Backbone:    MobileViT-S pretrained
Input:       256 x 256
Epochs:      25 for final runs
Seed:        1024
Optimizer:   Adam
LR:          1e-4
Scheduler:   cosine
Selection:   validation accuracy only
Test:        one locked evaluation after training
Fine-tuning: none on target datasets
~~~

Do not compare a 5-epoch pilot against the 25-epoch baseline as a final result. Pilots are only for detecting implementation bugs and choosing which candidates deserve a full run.

## 7. Pilot and final-run strategy

### Pilot stage

For each candidate:

- run the smoke test;
- train for 5 epochs;
- use the same seed and data split;
- save resolved config, stdout log, and checkpoint;
- verify that loss decreases and validation metrics are finite.

Pilot command pattern:

~~~powershell
python train.py --config configs/<candidate>.yaml --epochs 5 --output-dir runs/<candidate>_pilot
~~~

The exact command should be checked with:

~~~powershell
python train.py --help
~~~

### Final stage

Run the baseline control and selected candidates for 25 epochs. Prefer two final candidates if time is limited; run all three if the rented GPU budget allows it.

Each final run must save:

- resolved YAML config;
- environment information;
- training stdout;
- metrics.jsonl;
- summary.json;
- checkpoint path outside GitHub;
- git commit SHA;
- dataset manifest/checksum identifier.

## 8. Evaluation matrix

| Model | FF++ c23 | FF++ c40 | FaceShifter | Celeb-DF v2 | DFDC | WildDeepfake | Cross-manipulation |
|---|---|---|---|---|---|---|---|
| WGN baseline | required | required | required | required | required | required | required |
| WGN + gradient | required | required | recommended | required | required | required | recommended |
| WGN + curriculum | required | required | recommended | required | required | required | required |
| WGN + temporal | required | recommended | optional | required | required | required | optional |

Primary decision metrics:

1. Celeb-DF video AUC, because it is the largest current baseline weakness.
2. Cross-manipulation average AUC.
3. FF++ c40 AUC, as a compression-robustness check.
4. WildDeepfake and DFDC video AUC.

A candidate is retained for further work only if:

- Celeb-DF video AUC improves by approximately 2 percentage points or more; and
- FF++ c23 AUC does not drop by more than 1 percentage point; and
- the improvement is not caused by target-dataset fine-tuning.
