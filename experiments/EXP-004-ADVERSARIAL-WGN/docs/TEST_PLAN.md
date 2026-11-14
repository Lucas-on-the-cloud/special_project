# EXP-004 V2 — Verification and test plan before laboratory execution

No full adversarial experiment should be launched until Gates T0–T5 pass. This document separates **software correctness**, **reproduction continuity**, and **scientific validity**.

## T0 — Repository and artifact identity

**Goal:** confirm the experiment is built on the frozen EXP-002 reference.

Required:
- Git commit recorded.
- `best.pt` SHA256 equals `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`.
- `FaceForensics++-official.json` exists and its SHA256 is recorded.
- restored processed-data files exist.
- no checkpoint/data files are added to Git.

Failure action: stop.

## T1 — CPU unit tests

Run:

```bash
python -m pytest experiments/EXP-004-ADVERSARIAL-WGN/tests -q
```

Tests must cover:

| Test | Expected behavior |
|---|---|
| DCT inverse | IDCT(DCT(x)) ~= x |
| Frequency-fusion weights | shape equals input and bounded |
| FGSM/PGD/Jia-FAA adaptation | output shape preserved; finite; RGB in [0,1]; L-inf budget respected |
| Attack direction | simple fake logit is reduced by fake-to-real FGSM |
| Model immutability | attack generation changes no model parameter |
| Pilot sampler | deterministic; contains Real and Fake; covers all four fake manipulation groups |
| Fooling metric | denominator includes only clean-correct Fake samples |
| Diagnostic comparison | same-tensor diagnostic produces zero drift (legacy diagnostic test) |

Any failed test blocks lab execution.

## T2 — Environment preflight

Run `lab_preflight.py`.

Must record:
- Python
- PyTorch / CUDA
- GPU
- TIMM / torchvision / NumPy / sklearn / Pillow / PyYAML
- repository/data/manifest/checkpoint paths

Expected WGN reproduction dependency versions are documented in EXP-002 requirements. Do not casually upgrade the environment to make EXP-004 run; version changes create a different experimental environment and must be recorded.

## T3 — Clean-reference gate (mandatory)

Before attacks:

```bash
python experiments/EXP-004-ADVERSARIAL-WGN/code/validate_clean_reference.py \
  --repo-root "$WGN_REPO_ROOT" \
  --checkpoint "$WGN_CHECKPOINT" \
  --manifest "$WGN_MANIFEST" \
  --data-root "$WGN_DATA_ROOT" \
  --output "$WGN_REPO_ROOT/exp04_runs/clean_reference.json"
```

Expected FF++ c23:
- frames = 11,200
- frame accuracy = 0.9391964285714286
- frame AUC = 0.9821176020408163

Default acceptance tolerance: absolute 0.001 (0.1 percentage point) for ACC and AUC.

Why this gate exists: if clean reproduction continuity is broken, an apparent attack effect may be caused by data, preprocessing, package, checkpoint or loading differences.

Failure action: stop and debug. Do not loosen tolerance simply to pass.

## T4 — 40-frame GPU smoke attack

Run `run_lab_linux.sh`.

Purpose only:
- exercise gradients through the entire WGN;
- verify no OOM/NaN;
- verify output files;
- verify adversarial tensors satisfy bounds;
- verify Real samples remain unchanged in primary protocol;
- verify fake samples receive perturbations;
- verify WGSA hooks produce finite diagnostics.

**Do not quote ASR from 40 frames as a research result.**

Manual checks:
1. `environment.json` identifies exact checkpoint/manifest.
2. per-frame JSONL contains both labels and four fake manipulation groups.
3. for Real records: `linf == 0`.
4. for attacked Fake: `linf <= epsilon`.
5. clean and attacked score fields are finite.
6. no training checkpoint is produced.

## T5 — Attack sanity and strength gate

Before locked full test:
- FGSM changes at least some eligible fake scores in the intended direction.
- PGD should not be systematically weaker than a one-step FGSM because of an implementation bug; if it is, diagnose optimization/step settings.
- Jia-FAA adaptation must generate nonzero valid perturbations on eligible Fake samples.
- At least one visual/numerical sample is inspected by saving locally (not Git) clean x, perturbation heatmap and x_adv.
- report PSNR/SSIM later if claiming imperceptibility; L-inf alone is not a perceptual-quality proof.
- attack hyperparameters are fixed using theory/prior work or a validation/development set, **not the final test results**.

If the Jia adaptation fails, it does not mean WGN is robust; it may mean the adaptation is weak.

## T6 — Locked full FF++ c23 attack

After T0–T5:
- frozen checkpoint
- official test split
- threshold 0.5 frozen
- Fake-only attack
- Real unchanged
- same attack parameters for all fake manipulation groups

Save:
- environment/config
- per-frame records
- summaries
- stdout/stderr
- SHA256 identifiers

Primary result:
`ASR_fake|clean_correct`.

Secondary:
- unconditional fake evasion
- clean AUC/ACC on same population
- attacked-Fake/clean-Real AUC/ACC
- DF/F2F/FS/NT stratified results
- subband/gate/attention drift

## T7 — Statistical postprocessing

Use `analyze_by_video.py`.

Report:
- video-level score aggregation;
- fake-evasion ASR at frame and video levels;
- manipulation-specific results;
- bootstrap interval by video cluster.

Frames from one video are correlated; do not present a frame count as independent sample size.

## T8 — Mechanism validation before EXP-005

A high ASR answers RQ1 but not RQ2 causally.

Required follow-up controls before claiming WGSA-specific vulnerability:
- matched backbone-only detector trained/evaluated with the same protocol;
- original WGN vs constant/frozen gate ablation;
- successful vs unsuccessful attack comparison of WGSA statistics/gate/attention drift;
- attack-budget sweep;
- multiple PGD restarts / stronger adaptive evaluation.

Only if these support a WGSA/frequency-specific failure should EXP-005 architecture be motivated as a targeted defense.

## T9 — EXP-005 publication gate

A proposed defense must be compared with:
- unchanged WGN + standard adversarial training;
- defended WGN under **adaptive white-box attacks regenerated against the defense**;
- prior defense concepts where feasible;
- clean FF++ performance;
- cross-dataset / cross-compression generalization;
- parameter/FLOP/latency cost;
- ablations.

A defense that only reduces an old, non-adaptive attack is not sufficient evidence.

## Laboratory run checklist

Before run:
- [ ] pull exact Git commit
- [ ] restore private processed data
- [ ] restore public EXP-002 checkpoint
- [ ] T0 artifact hashes verified
- [ ] T1 pytest pass
- [ ] T2 preflight pass
- [ ] T3 clean reference pass
- [ ] create a new run directory

Pilot:
- [ ] T4 smoke pass
- [ ] T5 attack sanity pass
- [ ] inspect artifacts

Full:
- [ ] parameters locked before test
- [ ] T6 full c23 complete
- [ ] T7 video analysis complete
- [ ] results reviewed before any EXP-005 training
