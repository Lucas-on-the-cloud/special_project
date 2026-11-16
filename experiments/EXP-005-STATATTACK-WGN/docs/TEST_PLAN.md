# EXP-005 verification gates

Status 2026-11-16: 49 combined CPU tests passed (12 EXP-005 plus 37 regression tests), including independent NumPy MMD/SciPy blur, exposure/zero-pixel gradients, manual noise-descent step, three-layer parallel mixture, reference cycling and transactional resume rollback. All four actual-WGN full clean gates and the 120-frame/method CUDA validation smoke passed. Full FF++, Celeb-DF-v2, DFDC and WildDeepfake runs completed; each per-dataset integrity/statistical audit passed. Feature/classifier equality, finite optimization, RGB feasibility, parameter/buffer immutability, VRAM fit, full coverage, paired clean predictions, bounds and reference schedule were verified. DFDC resume provenance records the narrow score-parity correction and preserved earlier runner snapshot. GPU smoke is a setup gate; the completed full-cohort reports are the research evaluation.

## G0 — Paper/source and named profile

Pin reviewed commit/PDF hashes; map every executable transformation/loss/update/clip to the source or a declared reconstruction decision. Resolve profile discrepancies in HOU-PAPER-AUDIT. Test final configuration validation rejects implicit defaults, unknown datasets, missing Real bank and mismatched reference/manifest/checkpoint identities.

## G1 — Transform and MMD correctness on CPU

- Exposure at zero coefficients/flow reproduces its input, including zero-valued pixels with finite values/gradients. Check polynomial basis, flow sampling/alignment and boundary handling against independent small examples.
- Spatially constant Gaussian agrees with an independent convolution reference under the declared parameterization/padding; weights normalize correctly, stay finite and remain differentiable. Test variable blur maps and near-zero/extreme parameters.
- Additive noise, total RGB bounds and[0,1] feasibility are measured after composition, not only on intermediate noise. Test exposure/blur interactions and final cumulative MStat bounds.
- Compute MMD independently on tiny fixed feature matrices. Check same-set zero within tolerance, permutation invariance, nonzero input gradients, detached-bandwidth policy and degenerate/all-identical features. Final n+n and n=1 cases are finite; reject unequal batches unless a separately audited estimator is selected.
- One manual descent update has the declared sign and parameter learning rates. Count40 updates exactly; do not require every iteration's classifier score to improve under an MMD objective.
- MStat weights sum to1, branches take the same previous-layer input and optimize jointly. Hand-check a small three-layer mixture; verify gradients reach all degradation parameters and mixture logits. Repeating StatAttack sequentially is not this test.

## G2 — Frozen WGN and population integrity

Feature adapter matches the actual pre-classifier pooled vector and logits. Fake features retain gradients, references are detached, hooks do not retain stale samples or leak across forwards. Strict checkpoint load, eval mode and parameter/buffer hashes are unchanged after attack. No unrequested normalization or demo Gaussian pre-blur.

Validate reference frames come from FF++ train Real; file/video disjoint from FF++ validation/test and not chosen by attack outcomes. Cache hashes match the frozen network and preprocessing. References have the same count as the current Fake batch; cycling a960-image bank must cover every eligible Fake without `zip` truncation, duplicate evaluation IDs or skipped tail batches.

Test ASR excludes Real/baseline FN, returns null for zero eligible, and clean/unattacked images keep their paired predictions. Canonical clean eligibility and its clean score remain sourced from EXP-004; when re-evaluating a sample under another CUDA batch shape, require the same class at threshold0.5 and record the rechecked score and absolute delta instead of demanding FP32 probability equality. A changed class is a hard stop. Test different control/attack groupings and both same-name IDs in different dataset namespaces.

## G3 — Full clean gates and validation-only GPU smoke

All four full cohorts match EXP-004 fingerprints and reference ACC/AUC within0.001; log numerical near-threshold differences. Run finite forward/backward through both attacks on FF++ validation only. Confirm controls are identical to attack initialization, not forced identity. Inspect selected float32/PNG examples and norm/quality outputs as a pipeline sanity check.

Benchmark approximately120 validation Fake frames for both methods, including reference-feature caching, objective/diagnostics, peak VRAM and estimated full cost. If changing grouping to fit16GB, document/revalidate exact MMD behavior and re-lock before any final test. Do not run EXP-005 GPU smoke concurrently with EXP-004.

## G4 — Resumption and final-result audit

Interrupt/replay a small validation queue at a batch boundary: state/reference cursor/RNG and final outputs must agree with an uninterrupted run under recorded numerical tolerance. Ensure completed batches are not duplicated and partial stages never report complete.

For each full method/dataset, verify expected IDs/labels/videos, clean pairing, eligibility/denominators, unmodified Real/FN, source/reference hashes, finite RGB/features/losses, final bounds and summary/per-frame consistency. MMD minimization does not justify a copied Jia best-logit invariant. Video/sequence aggregation and bootstrap clusters are checked against the metadata; results with omitted records stay incomplete.
