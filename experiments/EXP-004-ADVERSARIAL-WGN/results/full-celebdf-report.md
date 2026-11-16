# EXP-004 — Full Celeb-DF-v2 official-direct

Completion-marker timestamp (Asia/Taipei): 2026-11-15T22:03:47.062697+08:00

Full processed test manifest: 16,576 frames; 5,696 Real, 10,880 Fake; 518 video/sequence records.

FAA reconstruction: **7,946/8,278 clean-correct Fake → Real; ASR 95.99%.**

Clean frame AUC=0.646972, ACC=0.643822; clean gate passed with tolerance 0.001. Historical baseline is a continuity check, not an exact match to all paper results.

Frozen EXP-002 checkpoint, input preprocessing, attack settings, batch size and seed transfer unchanged from full DFDC. All test frames are evaluated; only clean-correct Fake frames are attacked. Real and baseline false-negative Fake frames remain unchanged. No training or test-set parameter selection.

| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |
|---|---:|---:|---:|
| fgsm | 1,487/8,278 | 17.96% | 0.527818 |
| pgd | 8,278/8,278 | 100.00% | 0.053736 |
| frequency-init-control | 1,518/8,278 | 18.34% | 0.553718 |
| jia-faa-reconstruction | 7,946/8,278 | 95.99% | 0.316733 |

FAA frame ASR 95% video/sequence-cluster bootstrap interval: 94.86–97.02%; 1,000 replicates. Exploratory: shared source/identity linkage is unavailable; frames and sequences can be dependent.
Video/sequence-level FAA ASR: 289/296 = 97.64% (mean score across selected frames).
Paired FAA minus initialization-control ASR: 77.65 percentage points; paired flip table and bootstrap interval are in the evidence JSON.

| Method | Mean finite PSNR (dB) | Mean SSIM | Runtime (s) |
|---|---:|---:|---:|
| fgsm | 36.116 | 0.851677 | 58.93 |
| pgd | 40.056 | 0.932787 | 1045.32 |
| frequency-init-control | 42.872 | 0.993225 | 41.02 |
| jia-faa-reconstruction | 43.122 | 0.993540 | 290.03 |

Quality conditions on clean-correct Fake. Infinite PSNR for unchanged images is excluded from finite averages; counts and extrema are preserved in JSON. SSIM does not establish imperceptibility. Pixel L∞=4/255 and global DCT L∞=0.1 have different units; ASR does not fairly rank their matched strength. FAA: block8, energy-proportion M, P-step0.01, 10 updates, first-evasion stopping; PGD: alpha1/255, 10 updates, five trajectories. Seed1024, batch32.

| FAA outcome | Frames | Gate MAE | Attention MAE | Variance MAE |
|---|---:|---:|---:|---:|
| success | 7,946 | 0.001512 | 0.132683 | 0.132151 |
| failure | 332 | 0.002338 | 0.146026 | 0.106531 |

FAA remains an explicit reconstruction of Jia, not author-verified exact reproduction. Diagnostics are descriptive associations, without causal attribution to WGSA. Evaluation covers cropped decoded inputs, not re-encoded videos. Dataset ASRs condition on different clean-correct populations and should not be interpreted as a pure dataset-difficulty ranking. EXP-005 remains outside scope.

Evidence: [compact JSON](full-celebdf-evaluation.json), [locked config](../code/configs/final_reconstruction_celebdf_full.json). Runtime: `exp04-runtime/runs/final_celebdf_full_reconstruction_001/`; per-frame evidence, source snapshots, examples and analyses stay outside Git. Cohort locked before attack in `exp04-runtime/cohorts/full_celebdf.json`.

All recorded identity, code continuity, eligibility, perturbation-bound and summary consistency audits passed.
