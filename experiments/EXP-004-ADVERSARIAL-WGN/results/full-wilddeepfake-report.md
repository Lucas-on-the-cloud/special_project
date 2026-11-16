# EXP-004 — Full WildDeepfake

Completion-marker timestamp (Asia/Taipei): 2026-11-16T02:20:39.576236+08:00

Full processed test manifest: 165,662 frames; 58,659 Real, 107,003 Fake; 806 video/sequence records.

FAA reconstruction: **82,059/88,521 clean-correct Fake → Real; ASR 92.70%.**

Clean frame AUC=0.709236, ACC=0.677337; clean gate passed with tolerance 0.001. Historical baseline is a continuity check, not an exact match to all paper results.

Frozen EXP-002 checkpoint, input preprocessing, attack settings, batch size and seed transfer unchanged from full DFDC. All test frames are evaluated; only clean-correct Fake frames are attacked. Real and baseline false-negative Fake frames remain unchanged. No training or test-set parameter selection.

| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |
|---|---:|---:|---:|
| fgsm | 21,134/88,521 | 23.87% | 0.531366 |
| pgd | 88,521/88,521 | 100.00% | 0.045555 |
| frequency-init-control | 20,281/88,521 | 22.91% | 0.569819 |
| jia-faa-reconstruction | 82,059/88,521 | 92.70% | 0.333713 |

FAA frame ASR 95% video/sequence-cluster bootstrap interval: 89.85–94.65%; 1,000 replicates. Exploratory: shared source/identity linkage is unavailable; frames and sequences can be dependent.
Video/sequence-level FAA ASR: 342/372 = 91.94% (mean score across selected frames).
Paired FAA minus initialization-control ASR: 69.79 percentage points; paired flip table and bootstrap interval are in the evidence JSON.

| Method | Mean finite PSNR (dB) | Mean SSIM | Runtime (s) |
|---|---:|---:|---:|
| fgsm | 36.125 | 0.848884 | 594.98 |
| pgd | 40.054 | 0.931582 | 11189.50 |
| frequency-init-control | 42.910 | 0.993214 | 508.16 |
| jia-faa-reconstruction | 43.172 | 0.993521 | 2897.15 |

Quality conditions on clean-correct Fake. Infinite PSNR for unchanged images is excluded from finite averages; counts and extrema are preserved in JSON. SSIM does not establish imperceptibility. Pixel L∞=4/255 and global DCT L∞=0.1 have different units; ASR does not fairly rank their matched strength. FAA: block8, energy-proportion M, P-step0.01, 10 updates, first-evasion stopping; PGD: alpha1/255, 10 updates, five trajectories. Seed1024, batch32.

| FAA outcome | Frames | Gate MAE | Attention MAE | Variance MAE |
|---|---:|---:|---:|---:|
| success | 82,059 | 0.001655 | 0.154100 | 0.119768 |
| failure | 6,462 | 0.002765 | 0.148899 | 0.093987 |

FAA remains an explicit reconstruction of Jia, not author-verified exact reproduction. Diagnostics are descriptive associations, without causal attribution to WGSA. Evaluation covers cropped decoded inputs, not re-encoded videos. Dataset ASRs condition on different clean-correct populations and should not be interpreted as a pure dataset-difficulty ranking. EXP-005 remains outside scope.

Evidence: [compact JSON](full-wilddeepfake-evaluation.json), [locked config](../code/configs/final_reconstruction_wilddeepfake_full.json). Runtime: `exp04-runtime/runs/final_wilddeepfake_full_reconstruction_001/`; per-frame evidence, source snapshots, examples and analyses stay outside Git. Cohort locked before attack in `exp04-runtime/cohorts/full_wilddeepfake.json`.

All recorded identity, code continuity, eligibility, perturbation-bound and summary consistency audits passed.
