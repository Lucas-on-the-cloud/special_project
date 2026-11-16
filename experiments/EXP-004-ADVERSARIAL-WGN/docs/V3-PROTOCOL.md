# EXP-004 V3 execution protocol

V3 is the active implementation for FF++/DFDC and the full Celeb-DF-v2 official-direct/WildDeepfake extension. V2 and its protocol remain archived provenance. V3 evaluates an **explicit reconstruction** of Jia FAA; it does not assert exact author-code equivalence. EXP-005 is outside scope.

## Reconstructed FAA definition

Inputs are the frozen WGN's RGB face crops, resized to 256×256 by the unchanged EXP-002 inference loader, represented in [0,1]. For each image, DCT-II is orthonormal and applied independently to nonoverlapping blocks in each RGB channel. Block size is recorded; 8 is a project setting.

The following algorithmic choices are executable in `code/jia_faa.py`:

1. Generate P uniformly in [0,1], independently per coefficient. Initialize the current and best images to the clean input. Freeze WGN weights and buffers in eval mode.
2. Construct M once per input using an explicitly selected policy. `energy-proportion` averages squared clean coefficients across spatial blocks and divides by the per-channel sum over coefficient positions; zero-energy channels use 1/block². `legacy-magnitude-max` retains the old mean-absolute/max-normalized, 0.1-floor heuristic. `uniform` is a control. **None is author-verified.** No M policy is selected implicitly.
3. At each update, compute DCT of the current image. Form its coefficients plus M*P, map to a feasible RGB image, and compute BCE with true Fake label=1.
4. Ascend P by step_size*sign(gradient with respect to P), and reconstruct from the same current coefficients with updated P. P accumulates over steps; it is not reset after each update.
5. Feasibility map: IDCT, clamp RGB to [0,1], calculate the DCT norm of the difference from the clean input, then uniformly contract the RGB difference toward the clean image until the specified frequency norm is satisfied. This preserves RGB feasibility. It is an explicit reconstruction choice, not an asserted Euclidean projection or official implementation.
6. Frequency `linf` is the maximum absolute coefficient change over all channels/blocks/coefficients in one image. Frequency `l2` is the corresponding global Euclidean norm. Epsilon and step size have explicit DCT/P units; values are never copied automatically from pixel-space budgets.
7. Retain each image's greatest true-label BCE across feasible iterates, including clean. Stop that image after its first Fake→Real prediction. Images already false negatives at baseline are unchanged. Exactly `steps` updates are allowed; this is the declared interpretation of the pseudocode loop count.

This preserves the DCT/fusion/gradient/IDCT structure while exposing the under-specified parts. The source table in `JIA-ALGORITHM-SPEC.md` remains authoritative about fidelity limitations. Author code/details, if later established, should be introduced as a separately identified method rather than silently replacing a published configuration.

## Controls and populations

FGSM and PGD use a pixel L∞ bound and Fake-label BCE ascent. PGD keeps the best per-image iterate, includes a clean-start trajectory, and adds random-start trajectories for further restarts. Frame logits, perturbations and gradients must be finite. Real and baseline false-negative Fake frames stay unchanged for this fake-evasion protocol.

The reported ASR is conditional Fake→Real evasion. Real images are excluded from its denominator, not counted as failed attacks with success=0. A Real image correctly classified before attack and misclassified as Fake afterward could count as success in a separate Real→Fake evaluation with its own eligibility, objective and denominator. That direction is not part of the currently locked runs; clean Real images supply the companion ACC/AUC population.

True-Fake BCE is evaluated as `softplus(-logit)`. This is mathematically BCE(label=1), with a stable backward computation for confident positive logits; the cancellation-prone `sigmoid(logit)-1` can otherwise give exactly zero FP32 gradients. A logit=40 regression test covers this failure.

`frequency-init-control` uses the identical M, U(0,1) initialization and feasibility map, with no gradient updates. It is a project control. Both frequency methods reset the torch seed to seed+2 immediately before iterating the same batches, pairing their initial P tensors. PGD uses seed+1. These seeds isolate method ordering. FAA retains clean as a candidate but does not separately retain the unmodified P0 initialization before its first update; it is therefore not guaranteed to outperform this control on every frame.

FF++ c23/c40 use the official video split and manifest, 40 Real frames/video and 10 Fake frames/video/manipulation. DFDC uses all frames of the restored locked manifest and the original EXP-002 loader. FF++ development attacks use validation. DFDC with only a test manifest receives no development tuning; first audit its clean cohort and transfer locked settings, or explicitly reserve a new development split and redefine the final cohort.

Every final attack run requires a protocol-lock JSON equal to the settings() dictionary and a passed clean-reference JSON identifying the same checkpoint, manifest and complete cohort. A lock records a decision; it does not prove original-author fidelity or matched strength across pixel/frequency budgets.

## Locked initial test schedule (2026-11-15)

The first evaluation uses `code/configs/final_reconstruction_ffpp.json` and `final_reconstruction_dfdc.json`, fixed before final attacks:

- FF++ c23: all 11,200 official test frames (5,600 Real and 5,600 Fake).
- DFDC: 1,000 Fake + 1,000 Real, explicitly chosen by the user; video-round-robin selection with seed 1024, without looking at attack success. Its clean continuity gate still covers all 132,116 frames.
- FGSM/PGD pixel epsilon=4/255; PGD alpha=1/255, 10 updates, 5 trajectories (one clean start and four random starts).
- FAA: block=8, energy-proportion M, global per-image DCT L∞ epsilon=0.1, P step=0.01, 10 updates, U(0,1) initialization and first-evasion stopping. These are project reconstruction settings, not verified author hyperparameters.
- Four methods: FGSM, PGD, frequency-init-control, jia-faa-reconstruction. Batch=32, workers=4, seed=1024.
- Runtime `cohorts/final_{ffpp,dfdc}.json` records identities and selected relative paths before attack; run metadata records the same portable fingerprint. No final-test parameter sweep or reselection is planned in this initial schedule.

Development smoke and a 200-frame batch benchmark passed before this schedule. The final 40-frame smoke includes the paired initialization control and example export. Visual inspection of saved clean/adversarial images is a pipeline sanity check, not a perceptual study.

## Full DFDC extension authorized after the initial report

On 2026-11-15, the user requested evaluation of all restored DFDC test records: 132,116 frames (63,265 Real / 68,851 Fake). The new lock `code/configs/final_reconstruction_dfdc_full.json` differs from the initial DFDC lock only in max_samples=0. All attack settings, seed, methods and checkpoint remain fixed; there is no test-result tuning. Pre-attack identities are stored in runtime `cohorts/full_dfdc.json`; output uses a fresh `runs/final_dfdc_full_reconstruction_001/` directory. The initial 2,000-frame run and report remain preserved. A changed population changes batch composition and random draws assigned to each image, so the full/cohort comparison is descriptive rather than a paired algorithm change.

## Full external extension authorized after full DFDC

The user requested both remaining external datasets in full on 2026-11-15. Celeb-DF-v2 uses only the official-direct 518-video test cohort (16,576 frames: 5,696 Real / 10,880 Fake); the archived DeepfakeBench Celeb-DF copy is not substituted. WildDeepfake uses all 165,662 processed test frames (58,659 Real / 107,003 Fake). Full means the locked processed test manifests, not train/validation or every original video in a release.

`code/run_external_full.py` writes configs `final_reconstruction_{celebdf,wilddeepfake}_full.json` and runtime cohort files `cohorts/full_{celebdf,wilddeepfake}.json` before attack. Only the dataset selector differs from full DFDC; checkpoint, attack algorithms, preprocessing, methods, batch32, workers4, seed1024 and all budgets remain fixed. No dataset-specific parameter tuning or training. Input adapters, restoration, CLI dataset validation and descriptive cluster metadata are extended; core attack/quality/diagnostics source hashes must match full DFDC. CPU tests include both new test-only adapters.

Each full cohort must match the historical EXP-002 record fingerprint and clean ACC/AUC within absolute tolerance0.001 before attacks run. Full results use fresh `runs/final_{celebdf,wilddeepfake}_full_reconstruction_001/` folders; all four methods are postprocessed with 1,000 bootstrap replicates and audited by `summarize_external_full.py`. For both datasets, resampling uses video/sequence IDs; shared original-source or identity linkage is unavailable, so uncertainty intervals are exploratory. WildDeepfake sequence IDs must not be described as a count of independent original source videos. Different datasets have different clean-correct populations; their conditional ASRs alone do not rank dataset difficulty.

## Software smoke

`run_lab_linux.sh` runs CPU tests, verifies the complete clean FF++ c23 reference, then selects 40 validation frames for a three-step smoke. Its FAA frequency epsilon=0.1, step=0.01, norm=linf and energy-proportion M are **explicit software-check settings**, not author hyperparameters or selected final settings. Pixel controls keep their separate recorded pixel budget. Do not compare their smoke ASRs as evidence that one attack is stronger.

## Outputs and interpretation

- Conditional Fake→Real ASR with eligible and flipped counts; baseline false negatives are not new attack success.
- Clean and attacked-Fake/clean-Real frame ACC/AUC, plus video-level analysis.
- Per-frame pixel L∞, DCT L∞/L2, MSE, PSNR and Gaussian SSIM. PSNR=null means identical images/infinite PSNR. Neither L∞ nor SSIM alone establishes perceptual imperceptibility.
- Per-subband signed/absolute mean, variance, energy, gates and paired attention drift. The hook is disabled during inner optimization and enabled for paired clean/final diagnostics.
- `analyze_by_video.py` compares successful/unsuccessful attacks and clusters FF++ by official source pairs. DFDC intervals use video IDs unless better linkage is available and must be described as exploratory.
- Git commit, code SHA-256 (including new/untracked Python modules), tracked diff, package versions, seed, manifest/cohort/checkpoint identities, runtime and peak allocated VRAM.

The outcome may be positive or negative. A low ASR from this reconstruction can reflect optimization/M/budget choices; it is not a robustness certificate. Gate/attention drift is an association, not causal attribution to WGSA. Stronger attacks and matched trained controls are required before broader claims.
