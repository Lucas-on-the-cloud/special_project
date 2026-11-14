# EXP-005 — Reliability-Calibrated Wavelet Gating (RCWG)

**Status: module hypothesis and CPU-testable prototype; no adversarial defense validation or novelty claim yet.**

## Motivation
WGSA uses four signed global Haar subband means for the adaptive MLP and IDWT spatial attention. EXP-004 must first determine whether frequency perturbations cause measurable gating instability, whether it causes classification failures, and whether WGSA rather than the backbone is responsible.

## Candidate module
Keep MobileViT-S, Haar DWT/IDWT, original MLP and fusion/classifier. Add four descriptors per wavelet subband: signed mean, absolute mean, variance, normalized energy (16 numbers total). A two-layer MLP estimates four reliability values. Calibrate the original subband gates by

```
gate_new = gate_original * (1 + 0.5*tanh(residual_scale)*(2*reliability - 1))
```

The learnable residual scale initializes to zero, yielding an **exact original-WGSA forward output** at step zero. This is an ablation-friendly initialization, **not** evidence of robustness. Differentiable reliability scores can themselves be attacked.

## Integration
Restore original `WaveletGuidedNetwork` and strict-load EXP-002 weights first, then:

```python
from reliability_wgsa import attach_to_wgn
model = attach_to_wgn(model)
```

Create optimizer only after replacing WGSA, and include new model parameters. EXP-003 common.make_model does not know RCWG: a separate audited trainer is required before GPU defense training. Do not overwrite EXP-002 checkpoints.

Unit test:
```bash
python -m pytest experiments/EXP-005-ROBUST-WGSA/code/test_reliability_wgsa.py -q
```

## Proposed experiment sequence
E5-0: original EXP-002 checkpoint and EXP-004 attacks.
E5-1: identity-only RCWG sanity check.
E5-2: RCWG clean-only matched training.
E5-3: RCWG adversarial training with strong pixel PGD.
E5-4: **critical control**: original WGSA plus standard PGD adversarial training.
E5-5: ablations of mean, abs-mean, variance, energy, residual calibration and optional consistency loss.

Recompute adaptive attacks on the fully defended network with multiple restarts, matched attack budgets and held-out attack variants. Report clean/robust and cross-dataset AUC, fake-to-real ASR, parameter count, FLOPs and inference latency, video-cluster uncertainty. Do not optimize on the held-out test set.

## Prior art
Frequency ensembles (D4, WACV 2024), higher-order frequency moment defenses (Shahjahan et al., USENIX Security 2026) and frequency consistency approaches already exist. Novelty requires a demonstrated WGN-specific failure and a distinct mechanism validated against these baselines. See docs/RESEARCH-PROPOSAL.md.
