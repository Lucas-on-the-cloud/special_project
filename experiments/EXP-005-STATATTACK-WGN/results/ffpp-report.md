# EXP-005 — Full ffpp

full processed test; canonical Fake-to-Real eligibility; frozen WGN; train-Real-guided adaptation

StatAttack source-adapted40; MStatAttack reconstruction; not original Hou table reproduction

Frames: 11,200; eligible Fake: 5,333.

| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |
|---|---:|---:|---:|
| stat-init-control | 6/5,333 | 0.11% | 0.984573 |
| mstat-init-control | 9/5,333 | 0.17% | 0.984415 |
| hou-statattack-wgn-adapted | 4,952/5,333 | 92.86% | 0.416864 |
| hou-mstatattack-reconstruction | 5,015/5,333 | 94.04% | 0.397656 |

Total pixel L∞≤60/255; each layer noise≤4/255; those are distinct. Optimized methods use40 updates; MStat has3 layers. MMD, reference access and budgets differ from Jia; ASR alone does not rank equal strength. Real and baseline false-negative Fake are unchanged. Diagnostics are associations, without causal WGSA attribution. External sequence/video intervals remain exploratory without original-source linkage. BRISQUE was not evaluated; PSNR/SSIM and finite counts are in JSON.

[Compact evidence](ffpp-evaluation.json). [Algorithm specification](../docs/HOU-ALGORITHM-SPEC.md). All recorded coverage/reference/budget audits passed.
