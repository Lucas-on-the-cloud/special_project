# EXP-004 laboratory status

Updated:2026-11-16, Asia/Taipei. All four full test evaluations and audits completed. Active protocol: [V3](V3-PROTOCOL.md). EXP-005 is a separate study.

## Completed prerequisites

- Isolated Python 3.11.14 environment; torch 2.7.1+cu128, torchvision 0.22.1+cu128, timm 1.0.15, NumPy 1.26.4, scipy 1.13.1, sklearn 1.3.2, Pillow 10.2.0, PyYAML 6.0.1. All 47 installed packages compatible.
- RTX 4080 SUPER, 16 GB. Finite WGN input gradients; parameters/buffers unchanged. Batch-32 development benchmark peak allocation under 5.6 GiB.
- **35 CPU tests passed**: independent DCT, gradients/manual recurrence, final feasibility, stopping, immutability, sampling, DFDC, quality and numerical checks.
- Checkpoint SHA-256: `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`.
- Dataset revision: `e83e1c1d0b763f7fe324c5b57cd4c21e5f1529a2`. Seven shards checksum-verified. FF++ selected val/test c23: 22,400 images; DFDC: 132,116 images. All decoded. Historical baseline record fingerprints match after canonical Windows path reconstruction.
- HF API reports dataset public despite its name/documentation; visibility was not changed.
- Full clean gates passed with absolute tolerance 0.001:

| Dataset | Frames | Measured ACC | Measured AUC | Absolute ACC/AUC differences from EXP-002 |
|---|---:|---:|---:|---|
| FF++ c23 | 11,200 | 0.9391964286 | 0.9821022321 | 0 / 0.0000153699 |
| DFDC | 132,116 | 0.6359714191 | 0.6907695208 | 0.0000908293 / 0.0000215973 |

- Development: 40-frame validation smoke and 200-frame batch benchmark. Latest `development_ffpp_smoke_003` includes paired initialization control and examples. Bounds, scope and finite diagnostics passed; clean/adversarial example inspected. Pilot ASRs are not research results.
- Fixed FP32 Fake-BCE gradient cancellation using equivalent `softplus(-logit)`; regression test at logit=40.
- Final configurations locked in `../code/configs/`; cohort identities saved before attack. User chose DFDC 1,000 Fake + 1,000 Real, seed 1024; FF++ uses all 11,200 test frames.

## Evaluation stage

Full Celeb-DF-v2 official-direct (16,576 frames; 5,696 Real / 10,880 Fake) completed with all audits passed: FAA7,946/8,278=95.99%, control1,518/8,278=18.34%, PGD100%, FGSM17.96%. Clean ACC0.643822394/AUC0.646971575. [Report](../results/full-celebdf-report.md), [evidence](../results/full-celebdf-evaluation.json).

Full WildDeepfake (165,662 frames; 58,659 Real / 107,003 Fake) completed with all audits passed: FAA82,059/88,521=92.70%, control20,281/88,521=22.91%, PGD100%, FGSM23.87%. Clean ACC0.677336987/AUC0.709236493; FAA frame AUC0.333712762. FAA95% video/sequence-cluster interval89.85–94.65% is exploratory. [Report](../results/full-wilddeepfake-report.md), [evidence](../results/full-wilddeepfake-evaluation.json).

Both use full-DFDC core attack/quality/diagnostic hashes and settings unchanged; full cohort identities match archived EXP-002 references. Twelve unique archive shards are verified across the four datasets; all selected media decoded.37 EXP-004 CPU tests passed; combined EXP-004/005 suite49 tests passed. Extension queue completed2026-11-16,02:31:12 Asia/Taipei. [Four-dataset overview](../results/cross-dataset-overview.md). EXP-005 automatically started clean gates at02:31:21 after successful completion. Status files/logs remain outside Git in their respective runtime roots.

Initial final evaluation and postprocessing **completed**. Four methods: FGSM, PGD (10 updates, five trajectories), paired no-gradient frequency initialization and FAA reconstruction (10 updates). Both runs have `complete=true` and pass paired cohort/config/scope/budget audits. Common attack/evaluation source hashes match between datasets. No training was performed.

The user-authorized full DFDC extension **completed**, including postprocessing and audits, on all 132,116 restored test frames (63,265 Real / 68,851 Fake), with unchanged attack settings and seed; only max_samples changes to 0. Separate lock: `../code/configs/final_reconstruction_dfdc_full.json`. Runtime output: `runs/final_dfdc_full_reconstruction_001/`.

| Full DFDC method | Flips / eligible | Conditional ASR |
|---|---:|---:|
| FGSM | 23,731/42,932 | 55.28% |
| PGD | 42,932/42,932 | 100% |
| Frequency initialization | 9,617/42,932 | 22.40% |
| FAA reconstruction | 36,072/42,932 | 84.02% |

Full FAA 95% video-cluster bootstrap interval: 82.47–85.56%, exploratory because original-source linkage is missing. Paired FAA/control gain: 61.62 percentage points. FAA PSNR finite mean=43.236 dB, SSIM mean=0.991080. Full clean ACC/AUC exactly match the earlier complete clean gate. All sources, checkpoint and manifest hashes match recorded evidence. [Full report](../results/full-dfdc-report.md), [full evidence](../results/full-dfdc-evaluation.json).

Initial FF++ / 2,000-frame DFDC results remain preserved below:

| Method | FF++ conditional ASR | DFDC 2,000-frame cohort ASR |
|---|---:|---:|
| FGSM | 58.48% (3,119/5,333) | 55.28% (335/606) |
| PGD | 100% (5,333/5,333) | 100% (606/606) |
| Frequency initialization | 6.08% (324/5,333) | 23.60% (143/606) |
| FAA reconstruction | 51.21% (2,731/5,333) | 83.50% (506/606) |

See [results report](../results/README.md) and [compact evidence](../results/initial-evaluation.json) for uncertainty, quality and mechanism observations. Pixel/frequency budgets do not establish matched strength. DFDC's 394 baseline false negatives are excluded from conditional ASR, not counted as attack success.

FAA is an explicit reconstruction: M, norm/budget and RGB feasibility choices have not been verified against author code. This limits comparisons with Jia's paper.

## Evidence outside Git

Runtime root: `/home/naeem/Downloads/s1123570_sp1/exp04-runtime`.

| Relative location | Evidence |
|---|---|
| `environment-freeze.txt`, `environment-verification.json` | Environment and GPU checks |
| `cpu-tests.xml` | Test report |
| `data-restoration.json` | Pinned revision, shard integrity and complete decoding |
| `checkpoints/baseline_final/best.pt` | Frozen victim |
| `data/` | Verified manifests and media |
| `cohorts/final_{ffpp,dfdc}.json` | Pre-attack records, counts, fingerprints and config hashes |
| `cohorts/full_dfdc.json` | Pre-attack complete DFDC cohort and full config hash |
| `runs/clean_ffpp_c23.json`, `runs/clean_dfdc.json` | Complete passed clean gates |
| `runs/development_ffpp_smoke_003/` | Latest software smoke and examples |
| `runs/final_{ffpp,dfdc}_reconstruction_001/` | Final settings, source snapshots, per-frame metrics, examples and completion marker |
| `runs/final_dfdc_full_reconstruction_001/` | Complete full DFDC run, four method analyses and raw evidence |
| `sources/jia-cvpr2022.pdf` | Official CVF source |

Media, weights, raw per-frame logs and face examples remain outside Git. Compact summaries and reports belong in the experiment results directory.
