# EXP-005 — Full celebdf

full processed test; canonical Fake-to-Real eligibility; frozen WGN; train-Real-guided adaptation

StatAttack source-adapted40; MStatAttack reconstruction; not original Hou table reproduction

Frames: 16,576; eligible Fake: 8,278.

| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |
|---|---:|---:|---:|
| stat-init-control | 1/8,278 | 0.01% | 0.722517 |
| mstat-init-control | 5/8,278 | 0.06% | 0.728282 |
| hou-statattack-wgn-adapted | 7,666/8,278 | 92.61% | 0.139893 |
| hou-mstatattack-reconstruction | 7,795/8,278 | 94.17% | 0.128168 |

Total pixel L∞≤60/255; each layer noise≤4/255; those are distinct. Optimized methods use40 updates; MStat has3 layers. MMD, reference access and budgets differ from Jia; ASR alone does not rank equal strength. Real and baseline false-negative Fake are unchanged. Diagnostics are associations, without causal WGSA attribution. External sequence/video intervals remain exploratory without original-source linkage. BRISQUE was not evaluated; PSNR/SSIM and finite counts are in JSON.

[Compact evidence](celebdf-evaluation.json). [Algorithm specification](../docs/HOU-ALGORITHM-SPEC.md). All recorded coverage/reference/budget audits passed.
