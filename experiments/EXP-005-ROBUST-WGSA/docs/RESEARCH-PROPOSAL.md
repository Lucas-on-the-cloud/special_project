# EXP-005: Proposed RCWG defense — research plan

## Scientific status
Reliability-Calibrated Wavelet Gating (RCWG) is an unvalidated design hypothesis. No conclusion about novelty or adversarial robustness is justified at this stage.

## Research hypothesis
H1: small adversarial perturbations may alter relative subband magnitude and variance while the original four signed-mean descriptors insufficiently capture this change. A trainable, low-overhead calibration using complementary statistics could reduce some failures.

## Method
MobileViT-S -> pooled guide -> Haar DWT -> original signed mean MLP gates.
In parallel: signed mean, absolute mean, variance and normalized energy for all four maps -> 16D descriptor -> 2-layer reliability MLP.
A bounded, zero-initialized residual scale calibrates four original gates -> IDWT -> spatial attention -> unchanged feature fusion and classifier. Control for added parameter count with a size-matched arbitrary MLP.

## Research stage gates
- G0: EXP-004 shows meaningful evasion at declared pixel L-infinity budgets.
- G1: establish mechanism with backbone-only, frozen/neutral gate and original WGSA comparisons; drift alone does not prove causation.
- G2: train RCWG only if a WGSA-specific failure is supported; compare with standard PGD adversarial training on original WGSA.
- G3: adaptive white-box attacks against entire defended model, multiple restarts, pixel/DCT/hybrid attacks and unseen variants.
- G4: evaluate clean accuracy/AUC, robust AUC, fake-evasion ASR, cross-dataset performance, FLOPs, parameters, latency and per-video confidence intervals; check novelty against prior studies.

## Literature boundaries
- Jia et al. CVPR 2022: DCT frequency attacks and hybrid meta-learning attacks.
- Hou et al. CVPR 2023: statistical attacks and distribution-aware objectives.
- Abdullah et al. IEEE S&P 2024: evolving threats, generalization and vulnerability evaluation.
- Hooda et al. WACV 2024: disjoint frequency ensemble defense.
- Shahjahan et al. USENIX 2026: higher-order DCT moment pooling, noise residuals and semantic-disruption defense.

Our current probes are not exact copies of Jia or Hou. RCWG is not a certified defense. If G0/G1 fail, revise the hypothesis rather than claim improvement.
