# EXP-005 — Full dfdc

full processed test; canonical Fake-to-Real eligibility; frozen WGN; train-Real-guided adaptation

StatAttack source-adapted40; MStatAttack reconstruction; not original Hou table reproduction

Frames: 132,116; eligible Fake: 42,932.

| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |
|---|---:|---:|---:|
| stat-init-control | 2,606/42,932 | 6.07% | 0.739963 |
| mstat-init-control | 1,564/42,932 | 3.64% | 0.736311 |
| hou-statattack-wgn-adapted | 40,295/42,932 | 93.86% | 0.264679 |
| hou-mstatattack-reconstruction | 40,876/42,932 | 95.21% | 0.259296 |

Total pixel L∞≤60/255; each layer noise≤4/255; those are distinct. Optimized methods use40 updates; MStat has3 layers. MMD, reference access and budgets differ from Jia; ASR alone does not rank equal strength. Real and baseline false-negative Fake are unchanged. Diagnostics are associations, without causal WGSA attribution. External sequence/video intervals remain exploratory without original-source linkage. BRISQUE was not evaluated; PSNR/SSIM and finite counts are in JSON.

[Compact evidence](dfdc-evaluation.json). [Algorithm specification](../docs/HOU-ALGORITHM-SPEC.md). All recorded coverage/reference/budget audits passed.
