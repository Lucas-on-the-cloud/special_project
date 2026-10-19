# EXP-001 — DFD-HR fresh-training reproduction

**Status:** Planned; not run yet  
**Compute:** EZYCLOUDX Docker rental, 1 × Tesla V100-SXM2 32 GB, 94 GB RAM, 450 GB storage  
**Paper:** [DFD-HR, CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/papers/Sun_DFD-HR_Generalizable_Deepfake_Detection_via_Hierarchical_Routing_Learning_CVPR_2026_paper.pdf)  
**Official code:** [Disguiser15/DFD-HR](https://github.com/Disguiser15/DFD-HR)  
**Pinned upstream commit:** ec85fc462d06f06448d2222748e24e7113f25784

## Goal

Reproduce the official DFD-HR training pipeline using the paper's training dataset and configuration, then evaluate the resulting model using the paper's cross-dataset protocol. This is Stage 1. The student's own dataset is reserved for Stage 2, after the reproduction is checked.

We will use the official code at the pinned commit. We will **not** initialize the model from the authors' released DFD-HR final checkpoint.

Important initialization detail: the official implementation loads the pretrained OpenAI CLIP ViT-L/14 visual backbone, freezes its parameters, and trains the newly initialized DFD-HR components (routers, adapters, query token, and classifier). In this project, “train from the start” means training a fresh DFD-HR model without the released DFD-HR checkpoint; it does not mean randomly initializing the CLIP backbone. This matches the official implementation.

## Official setup to reproduce

| Setting | Official value |
|---|---|
| Training dataset | FaceForensics++ |
| Compression | c23 |
| Backbone | CLIP ViT-L/14, pretrained visual backbone |
| Input resolution | 448 × 448 |
| Frames per video | 8 for train and test |
| Training batch size | 16 |
| Optimizer | Adam, learning rate 0.0001, weight decay 0.0005 |
| Seed | 1024 |
| Metric | AUC |
| Configured epochs | 20 |
| GPUs | 1 |
| Evaluation example in official command | Celeb-DF-v2 |

The upstream training loop iterates from epoch 0 through nEpochs inclusively. We will record the actual number of passes shown in the logs and compare it with the paper's epoch definition before editing upstream code.

## Stages and gates

### 0. Confirm the rented machine

Run the read-only preflight script in this repository. Confirm GPU model, available disk, Python, PyTorch, and whether Conda is installed. Do not install packages or launch training until we review this output.

### 1. Pin and install the official code

EXP-001 is deferred. Its former root-level setup scripts were removed during the repository cleanup; if this experiment resumes, recreate the environment tooling inside this experiment directory and pin the upstream commit and dependencies here.

### 2. Confirm dataset access and layout

The official repository recommends preprocessed face-cropped data following the DeepfakeBench format. Confirm legal access to FaceForensics++ c23 training data and Celeb-DF-v2 evaluation data first. Keep videos, frames, face crops, JSON manifests, and model weights on the rented storage or approved dataset storage; never commit them to this project repository.

The official configuration expects:
- RGB data under ./datasets
- dataset JSON manifests under ./preprocessing/dataset_json

Do not start full training until both paths and the selected split are verified. Record dataset source/version, split, number of videos, and number of frames used.

### 3. Smoke test

Before a full run:
- instantiate the official dataset and load one training batch;
- verify image tensor shape, labels, and that paths resolve;
- run one forward/backward optimizer step on the V100;
- record peak GPU memory and time per step.

This is only a pipeline check. It is not a reported reproduction result and must not be used to tune against the final held-out data.

### 4. Fresh training

From the official DFD-HR repository, run the official single-GPU command after dataset paths are verified:

~~~bash
conda run -n dfdhr-py310 python training/train.py \
  --detector_path ./training/config/detector/dfd_hr.yaml \
  --train_dataset FaceForensics++ \
  --test_dataset Celeb-DF-v2
~~~

Do not pass a DFD-HR checkpoint or a weights_path to this training command. The code will fetch the official pretrained CLIP backbone from Hugging Face. Capture the exact command, commit, config, console log, training duration, peak memory, and output checkpoint path.

The official training script evaluates the named test dataset during training. Before treating Celeb-DF-v2 as an untouched final test set, we must inspect the paper's split and checkpoint-selection protocol. Any data used for model selection must be labelled as validation; reserve a separate held-out set for the final project claim.

### 5. Evaluate and compare

After training completes, evaluate the saved model on the same datasets/splits as the paper where data access permits. Record at least AUC, accuracy, EER, average precision, sample count, checkpoint, and evaluation command. Report unavailable datasets as unavailable; do not substitute a different split silently.

### 6. Stage 2

Only after Stage 1 is documented, evaluate on the student's own approved data with a fixed, documented protocol. Keep Stage 2 results separate from paper-reproduction results.

## Result record

| Field | Value |
|---|---|
| Machine / GPU | Pending |
| OS and driver | Pending |
| Python / PyTorch / CUDA | Pending |
| Official code commit | ec85fc462d06f06448d2222748e24e7113f25784 |
| Dataset source / version / license | Pending |
| Train and evaluation splits | Pending |
| Actual epochs / runtime | Pending |
| Peak GPU memory | Pending |
| AUC / ACC / EER / AP by dataset | Pending |
| Checkpoint location (outside Git) | Pending |
| Deviations from paper | Pending |

## Important storage and cost rules

Do not put datasets, extracted frames, face crops, logs, or checkpoints in this GitHub repository. Keep a second copy of essential checkpoints and small result summaries in approved persistent storage before deleting the rented container. The rental renews by the hour, so stop or delete it when you are not using it for an extended period.

## Decision after EXP-001

- If the official data format and training pipeline work, keep DFD-HR as the first reproduced baseline.
- If data access or the official environment blocks training, record the exact blocker before selecting a fallback.
- Do not start WGN implementation until the DFD-HR smoke test and data access are understood.
