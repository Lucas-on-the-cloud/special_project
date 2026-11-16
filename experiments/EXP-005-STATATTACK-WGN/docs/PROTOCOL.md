# EXP-005 active source-adapted40 protocol

Status2026-11-16: completed on the four full cohorts; all per-dataset audits passed. [Locked profile](../code/configs/hou_source_adapted_40.json) and [executable specification](HOU-ALGORITHM-SPEC.md) resolve the reviewed source/paper differences. See [PLAN](../PLAN.md), [full-cohort results](../README.md#full-cohort-results) and [source audit](HOU-PAPER-AUDIT.md). This profile is an explicit WGN adaptation, not exact author experiment reproduction.

## Victim and populations

- Frozen EXP-002 MobileViT-S+WGSA checkpoint SHA256 `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`. Strict load; eval mode; no parameter/buffer updates.
- EXP-002 RGB crop loader: resize256×256, ToTensor[0,1], no extra normalization, Gaussian pre-blur, JPEG or augmentation. All four full test cohorts/fingerprints are inherited from EXP-004.
- Real0/Fake1, threshold0.5. Eligibility is Fake with canonical clean score≥0.5; success is attacked score<0.5. Real and clean false-negative Fake stay unchanged. Report both eligible and total Fake counts.
- Source-reference policy: seed1024, proposed960 FF++ train-only Real frames chosen video-round-robin. Cache frozen global-pool features; lock IDs, image/reference-feature hashes and exact assignment. No best-reference selection by test success. Same bank across datasets/methods.
- All records appear once in evaluation; references can be reused and do not add evaluation samples. Pack eligible Fake separately for batch-coupled optimization. Evaluation/diagnostics remain paired by stable frame ID.

## Scheduled parameter profile

| Item | Scheduled value | Provenance / decision |
|---|---|---|
| Input size | 256×256 RGB | Fixed WGN contract |
| Optimization steps | 40, main paper | Tested update count, not41 updates |
| StatAttack composition | exposure→adaptive blur→noise | Required mechanism |
| MStatAttack | 3 sequential layers; parallel exposure/blur/noise/identity mixture in each | Explicit reconstruction; no upstream MStat implementation in reviewed tree |
| Optimization grouping | 30 Fake +30 Real references; n+n for final partial | Paper MStat batch size transferred to both methods for controlled comparison |
| Exposure model | degree11 polynomial, shared RGB field, tune_scale8 | Source-style flow sampling; log-field numerical clamp±20 declared in spec |
| Exposure learning rate | 0.1 | Source default retained; differs from supplement0.01 |
| Spatial flow learning rate | 0.001 | Supported by supplement/source |
| Gaussian kernel | 3×3, source precision-squared exponent, reflection padding | Initial precision100/sqrt(3HW) per image |
| MMD estimator | five Gaussian kernels, multiplier2, detached empirical bandwidth, floor1e-12 | Independent NumPy and degenerate tests pass |
| Regularization | 10*MMD+10*rendered-field penalty+10*flow penalty | Positive source-style penalties; layer-average for MStat, no classification CE |
| Pixel total/noise bound | 60⁄255 and4⁄255 respectively | Source-style total bound transferred to each MStat layer relative to clean; distinct constraints |
| MStat mixture logits/rates/bounds | four per-image softmax logits/layer, init0, rate0.1 | Explicit reconstruction choice; jointly optimized |
| Momentum, blur/noise rates, clipping stage | momentum1, blur0.1, noise1/255; noise clipped after update; RGB after each layer | All values explicit in JSON/spec |
| Return/stopping | fixed-step final iterate; zero-update controls | No per-image first-evasion stop or classifier-best selection |
| Seeds/order/reference assignments | seed1024, explicit recorded order | Bank and batch order are part of the attack |

The proposed optimization minimizes feature MMD with the selected regularization. It does not add classifier CE by default. MMD is not per-image: removing an already-evaded image mid-batch changes other images' objective. A full batch/reference-assignment trace is required to replay attacks.

## Controls and comparisons

Core full methods: adapted StatAttack, reconstructed MStatAttack, each method's matching initialization-only control. A zero-update control reuses that method's composition, init, seeds, RGB feasibility and reference schedule; it is not called clean if its blur already changes the image.

Exposure-only/blur-only/noise-only and regularization/objective ablations are follow-up development checks, with final-test extensions explicitly locked before execution. A permutation of the same Real batch is **not** a meaningful MMD ablation because the distribution estimator is permutation invariant.

Reuse EXP-004 results only as a clearly labeled contextual comparison. Its pixel4⁄255/10-step controls and DCT0.1 FAA are different from Hou's reported pixel8⁄255/40-step baselines. A new Hou-baseline run, if needed, gets its own config and compute estimate; source total60⁄255 clipping also does not establish equal attack strength. Compare paired IDs, quality and cost, not ASR alone.

## Runtime and evidence

Separate EXP-005 runtime root; reuse read-only checkpoint/media and preserve EXP-004 source snapshots/results. Final locks record cohort/manifest/checkpoint/source/reference IDs+hashes, environment, bank access policy, MMD layer/kernel/reduction, batching, all learning rates/regularizers/bounds, iteration/selection behavior and seeds.

Log method, completed/total evaluation and eligible-attack counts, batch/reference IDs, objective components, norm/feasibility checks, runtime and VRAM. Checkpoint enough state for deterministic resume (batch boundary, assignment cursor, RNG and any ongoing optimizer state); stream metrics and selected float32 examples instead of storing a huge full float32 corpus. `complete=true` is written only after every requested record/method and all post-run audits pass. Partial failure remains visible.

Report clean and attacked-Fake/clean-Real ACC/AUC, conditional ASR, finite PSNR/SSIM, image/DCT norms, BRISQUE if validated, MMD changes, WGSA associations, video-level aggregation and source-cluster uncertainty. Lack of original-source/identity links makes external intervals exploratory. Do not claim black-box transfer, causal WGSA failure or a trained defense from these WGN-only runs.
