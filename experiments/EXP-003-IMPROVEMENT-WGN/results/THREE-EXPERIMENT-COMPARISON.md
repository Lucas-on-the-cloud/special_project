# EXP-003: comparison of three WGN generalization improvements

This record freezes the completed results from 19 October 2026 on `main`. The
three planned improvements are
gradient regularization, curriculum training, and temporal consistency. The
WGN model reproduced in EXP-002 is included as the common reference. The
`baseline_final` run name is retained only as an internal runtime identifier.

## Evaluation protocol

- FF++ c23 reports frame AUC on the in-domain test split.
- Celeb-DF v2 reports video AUC using videos from the official author archive,
  sampled to 32 frames and processed with the WGN MTCNN crop pipeline.
- DFDC and WildDeepfake report video AUC.
- The predeclared acceptance rule is a gain of at least 2.00 percentage points
  on Celeb-DF v2 official-direct while losing no more than 1.00 point on FF++
  c23.
- Values in parentheses are percentage-point changes from the EXP-002 reproduced reference.

## Results

| Method | FF++ c23 frame AUC | Celeb-DF v2 official video AUC | DFDC video AUC | WildDeepfake video AUC | Rule |
|---|---:|---:|---:|---:|:---:|
| WGN reproduced reference (EXP-002) | 98.21 | 70.14 | 69.67 | 71.54 | Reference |
| Gradient | 98.52 (+0.30) | 68.31 (-1.83) | 69.87 (+0.19) | 72.17 (+0.62) | Fail |
| Curriculum | 98.34 (+0.13) | 63.71 (-6.43) | 67.75 (-1.92) | 69.85 (-1.69) | Fail |
| Temporal consistency, lambda=0.10 | 98.58 (+0.37) | 71.03 (+0.89) | 68.89 (-0.78) | 71.72 (+0.17) | Fail |

None of the three planned improvements passes the selection rule. Gradient
regularization gives mixed cross-dataset results. Curriculum is rejected because
it reduces all three cross-dataset AUCs. Temporal consistency improves Celeb-DF
and WildDeepfake slightly, but reduces DFDC and does not reach the required
Celeb-DF gain.

The temporal control ablation, which uses paired temporal sampling with
`temporal_lambda=0`, gives 98.27 FF++ c23, 71.92 Celeb-DF, 70.78 DFDC, and 75.10
WildDeepfake. Its changes are +0.06, +1.78, +1.11, and +3.55 points respectively.
It is the strongest completed generalization signal, although it narrowly misses
the predeclared Celeb-DF threshold. This ablation indicates that paired temporal
sampling helped more than the lambda=0.10 consistency penalty. The reproduced
WGN reference and temporal control should remain the current finalists while degradation experiments
are evaluated.

## Portable checkpoints

All checkpoints below are stored in the public Hugging Face model repository.
No authentication is required. The hash records the exact weights used for the
results above; each GitHub artifact directory contains a `CHECKPOINT.json`
pointer with the same identity.

| Model | Best epoch | Bytes | SHA-256 | Checkpoint |
|---|---:|---:|---|---|
| WGN reproduced reference (EXP-002) | 20 | 23,203,811 | `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6` | [best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/best.pt) |
| Gradient | 24 | 26,562,737 | `9b372bb10f8244e3635c9c00e4d310382535cebd04b59399d34e0a054e0f52aa` | [best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/gradient_final/best.pt) |
| Curriculum | 20 | 23,203,875 | `3af3ee3e3b8fe283a105d1b31eb8a62df90ef5c1be387a5df5d7ed8a1794da7f` | [best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/curriculum_final/best.pt) |
| Temporal consistency | 16 | 23,203,811 | `9e8918e0721f57d15335be27f0739dc633797b8e191ac31447a9db9f4be58c65` | [best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/temporal_final/best.pt) |
| Temporal control ablation | 7 | 23,203,811 | `4f94e5147783d103ff058ca8f805f289a8938060f5a6fdab94f6cc3351750c92` | [best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/temporal_control_final/best.pt) |

The adjacent artifact directories also contain the resolved configuration,
environment record, per-epoch metrics, evaluation JSON, and checksum file. Raw
datasets and generated face crops are intentionally excluded because of their
size; restore them separately when moving machines.

## Restore on another machine

```powershell
git clone https://github.com/Lucas-on-the-cloud/special_project.git
cd special_project
git checkout main
C:\sp\.tools\hf-cli\Scripts\hf.exe download lucashwang0102/wgn-checkpoints `
  --local-dir C:\sp\checkpoint-handoff
Get-FileHash C:\sp\checkpoint-handoff\experiments\EXP-003-IMPROVEMENT-WGN\artifacts\gradient_final\best.pt -Algorithm SHA256
```

The machine-readable copy of this table, including full-precision metrics and
the temporal-control ablation, is in
[`THREE-EXPERIMENT-COMPARISON.json`](THREE-EXPERIMENT-COMPARISON.json).
