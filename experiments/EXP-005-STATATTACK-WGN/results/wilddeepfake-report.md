# EXP-005 — Full wilddeepfake

full processed test; canonical Fake-to-Real eligibility; frozen WGN; train-Real-guided adaptation

StatAttack source-adapted40; MStatAttack reconstruction; not original Hou table reproduction

Frames: 165,662; eligible Fake: 88,521.

| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |
|---|---:|---:|---:|
| stat-init-control | 17/88,521 | 0.02% | 0.786398 |
| mstat-init-control | 43/88,521 | 0.05% | 0.788021 |
| hou-statattack-wgn-adapted | 81,545/88,521 | 92.12% | 0.166888 |
| hou-mstatattack-reconstruction | 83,521/88,521 | 94.35% | 0.152379 |

Total pixel L∞≤60/255; each layer noise≤4/255; those are distinct. Optimized methods use40 updates; MStat has3 layers. MMD, reference access and budgets differ from Jia; ASR alone does not rank equal strength. Real and baseline false-negative Fake are unchanged. Diagnostics are associations, without causal WGSA attribution. External sequence/video intervals remain exploratory without original-source linkage. BRISQUE was not evaluated; PSNR/SSIM and finite counts are in JSON.

[Compact evidence](wilddeepfake-evaluation.json). [Algorithm specification](../docs/HOU-ALGORITHM-SPEC.md). All recorded coverage/reference/budget audits passed.
