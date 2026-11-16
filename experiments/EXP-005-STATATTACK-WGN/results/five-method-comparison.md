# EXP-004 / EXP-005 — comparison of five attacks

This table compares EXP-004's pixel-space controls and Jia FAA with EXP-005's Hou StatAttack and MStatAttack reconstruction. All methods use the same frozen EXP-002 WGN checkpoint and the same four full processed test cohorts. ASR is conditional frame-level Fake→Real evasion among frames WGN classified as Fake before attack; denominators are the canonical clean-correct Fake counts.

## ASR by full test cohort

| Dataset | Eligible Fake | FGSM | PGD | Jia FAA reconstruction | Hou StatAttack adaptation | Hou MStatAttack reconstruction |
|---|---:|---:|---:|---:|---:|---:|
| FF++ c23 | 5,333 | 58.48% | 100.00% | 51.21% | 92.86% | 94.04% |
| Celeb-DF-v2 official-direct | 8,278 | 17.96% | 100.00% | 95.99% | 92.61% | 94.17% |
| DFDC | 42,932 | 55.28% | 100.00% | 84.02% | 93.86% | 95.21% |
| WildDeepfake | 88,521 | 23.87% | 100.00% | 92.70% | 92.12% | 94.35% |

## Method summary and threat constraints

| Method | Domain / objective | Locked setting in these experiments | Fidelity note |
|---|---|---|---|
| FGSM | Pixel gradient sign against the Fake-label loss | One step; pixel L∞≤4/255 | EXP-004 control attack |
| PGD | Iterative pixel gradient sign against the Fake-label loss | 10 updates; five trajectories (one clean and four random starts); pixel L∞≤4/255 | EXP-004 control attack; retains best iterate |
| Jia FAA | Block DCT perturbation, frequency weighting and gradient updates | 8×8 block DCT; frequency L∞≤0.1; 10 updates; energy-proportion M | Explicit reconstruction of Jia et al.; under-specified M/norm choices are project decisions, not author-verified |
| Hou StatAttack | Exposure, adaptive blur and noise optimized to align fake/reference WGN feature distributions with MMD | 40 updates; total pixel L∞≤60/255; 960 FF++ train-Real references | Source-adapted WGN profile; not exact reproduction of Hou's original tables |
| Hou MStatAttack | Three sequential layers, each mixing exposure/blur/noise/identity, optimized with distributional objective | Three layers; 40 joint updates; total pixel L∞≤60/255; same reference bank | Explicit reconstruction because the reviewed author repository did not contain MStatAttack implementation |

The budgets/objectives are not matched: pixel L∞, DCT L∞, number of updates, random restarts and distributional objectives differ. The ASR ranking therefore describes these locked configurations, not equal-strength methods. PGD's 100% result should be read with its specified pixel budget and 10-step/five-trajectory search. Hou initialization-only controls measure evasion caused by initial transforms without optimization; their ASRs are 0.11%/0.17% (FF++), 0.01%/0.06% (Celeb-DF), 6.07%/3.64% (DFDC), and 0.02%/0.05% (WildDeepfake), for Stat/MStat respectively. Jia's paired frequency initialization control is in the detailed EXP-004 tables.

These are processed face-frame evaluations; the full original-video re-encoding pipeline was not tested. Results support vulnerability of this frozen WGN to these white-box configurations. They do not establish causal WGSA attribution, generalize to every detector, or constitute an exact reproduction of the two papers.

## Source tables and reports

- [Complete EXP-004 tables](../../EXP-004-ADVERSARIAL-WGN/results/tables/COMPLETE-TABLES.md) include per-method flips, confidence intervals, quality, runtime, video/sequence and manipulation summaries.
- [EXP-005 full-cohort summary](../README.md#full-cohort-results) and its [FF++](ffpp-report.md), [Celeb-DF](celebdf-report.md), [DFDC](dfdc-report.md) and [WildDeepfake](wilddeepfake-report.md) reports provide per-method counts, AUC and quality summaries.
- [EXP-004 protocol](../../EXP-004-ADVERSARIAL-WGN/docs/V3-PROTOCOL.md), [Jia specification](../../EXP-004-ADVERSARIAL-WGN/docs/JIA-ALGORITHM-SPEC.md) and [Hou algorithm specification](../docs/HOU-ALGORITHM-SPEC.md) record implementation details and fidelity boundaries.
