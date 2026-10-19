# Experiment backup and machine handoff

This document defines what must be preserved on GitHub after every research
experiment. The goal is to move to a new machine without losing the result,
the selected model, or the context needed to interpret and continue the work.

## Completion rule

A final experiment is complete only when another machine can answer all of the
following from the repository:

1. What hypothesis and control did the run test?
2. Which code, configuration, dataset split, preprocessing, and seed were used?
3. Which checkpoint was selected, and by which validation criterion?
4. What happened during training and locked evaluation?
5. Can the selected model be downloaded and used without retraining?
6. Can every committed artifact be checked for corruption?

Finishing epoch 25 locally is not completion. The handoff package must be
committed, pushed to `main`, and verified against the remote branch.

## Required final-run package

Every final baseline, control, and candidate must have an artifact directory
inside its owning experiment:

```text
experiments/EXP-XXX/artifacts/<run-name>/
├── README.md
├── best.pt
├── resolved_config.yaml
├── environment.json
├── metrics.jsonl
├── progress.json
├── summary.json
├── evaluation.json
├── training.log
├── evaluation.log
├── source.patch
├── SHA256SUMS.txt
└── ARTIFACT-MANIFEST.json
```

Method-specific files such as a curriculum difficulty cache or a
cross-manipulation result must be included when they affect interpretation or
allow an expensive step to be reused.

### Checkpoint

- `best.pt` is mandatory for every final run. It is the portable inference and
  evaluation checkpoint selected using validation data.
- Record its SHA-256 in both `SHA256SUMS.txt` and the artifact manifest.
- Verify that the Git blob on remote `main` matches the local checkpoint.
- A checkpoint below 95 MiB may be committed directly. Larger checkpoints must
  use Git LFS or a GitHub Release asset; commit its URL and checksum.

`last.pt` contains optimizer, scheduler, and RNG state for resuming unfinished
training. Do not commit it after every epoch because normal Git history retains
every large version. When an unfinished run must move machines, upload one
explicit resume snapshot through Git LFS or a GitHub Release and record its
checksum. After a final run completes, `best.pt` is the required portable file.

### Configuration and source identity

- Save the fully resolved configuration, including command-line overrides.
- Save the Git commit used when training started.
- Save `source.patch` when the working tree was dirty. An empty patch confirms
  that the recorded commit fully identifies the source.
- Record the exact training command in `training.log`.
- Describe the hypothesis, control, and selection rule in the experiment plan.

### Dataset identity

- Record dataset name, release/version, official source, and access conditions.
- Preserve train/validation/test split files and preprocessing code.
- Record SHA-256 for the training manifest and every evaluated manifest.
- Record label mapping, video identifier rules, frame sampling, face crop
  method, resolution, and compression level.
- Do not commit licensed videos, extracted frames, credentials, or download
  tokens. The repository must contain instructions for acquiring them again.

### Environment

`environment.json` must include Python, PyTorch, CUDA, torchvision, model
library versions, GPU model, operating system, precision, batch sizes, source
commit, and training-manifest checksum. A lock file may be added when exact
package resolution is otherwise difficult.

### Training and evaluation evidence

- Preserve per-epoch training and validation metrics in a machine-readable
  format such as JSONL.
- Preserve the best epoch, validation selection metric, wall time, and final
  completion status.
- Preserve final evaluation metrics per dataset, frame/video counts, aggregation
  level, and the evaluated checkpoint checksum.
- Keep locked target evaluation separate from pilot and validation results.
- Save prediction files when later metric recomputation is important and their
  size is reasonable. Otherwise retain aggregate metrics and manifest identity.
- Preserve final training and evaluation logs. Transient watchdog heartbeats do
  not need to be committed.

## What belongs in GitHub

| Item | Normal Git | LFS/Release | Keep external |
|---|---:|---:|---:|
| Source, configs, split files, documentation | yes | no | no |
| Metrics, summaries, logs, checksums, manifests | yes | no | no |
| Final `best.pt` below 95 MiB | yes | optional | no |
| Larger checkpoint or mid-run `last.pt` | no | yes | temporary local copy |
| Licensed videos and generated face crops | no | no | yes |
| Secrets, tokens, signed URLs | never | never | secure credential store |

Pilot runs used only as smoke checks need their config, outcome, and failure
reason. Their checkpoints do not need to be committed unless the pilot exposes
a result required for later analysis.

## Required workflow

### Before training

1. Create or update the experiment plan and frozen comparison protocol.
2. Commit the source and configuration, or ensure the runner captures a patch.
3. Validate the dataset manifest and record its checksum.
4. Run a real-data smoke test covering CUDA forward/backward, optimizer update,
   checkpoint round trip, and one validation batch.

### During training

1. Write metrics and `last.pt` atomically after each completed epoch.
2. Maintain a status file with run name, phase, PID, completed epochs, and log.
3. Use a resume-safe runner and watchdog for unattended work.
4. Never overwrite a locked evaluation created from a different checkpoint or
   dataset manifest.

### After a final run

1. Select `best.pt` using the declared validation criterion.
2. Run the common locked evaluation suite once.
3. Build the portable artifact package and experiment registry.
4. Commit and push to `main`.
5. Compare local and remote commit SHA and verify the committed checkpoint blob.
6. Mark the experiment complete only after remote verification succeeds.

## Restoring on another machine

1. Clone `main` and read the root README, experiment README, plan, result table,
   and experiment registry.
2. Download datasets from their official sources and rebuild them with the
   committed preprocessing code.
3. Verify dataset manifests against the recorded checksums.
4. Recreate the recorded Python/PyTorch/CUDA environment.
5. Verify `best.pt` against `SHA256SUMS.txt`.
6. Run a smoke inference before any full evaluation or resumed training.
7. Use `last.pt` only when continuing an unfinished run; use `best.pt` for final
   inference and comparison.

## EXP-003 implementation

EXP-003 automates this policy through
[`publish.py`](../experiments/EXP-003-IMPROVEMENT-WGN/code/publish.py). Each
final publication packages the portable files, assembles logs, writes checksums
and `ARTIFACT-MANIFEST.json`, updates the experiment registry and result table,
commits to `main`, pushes, and verifies both the remote commit and checkpoint
blob. Existing completed runs can be migrated with:

```powershell
C:\sp\.tools\py311\python.exe `
  experiments\EXP-003-IMPROVEMENT-WGN\code\publish.py `
  --backfill-exp003
```

New degradation runs in the active queue use the same publication path
automatically when they finish.
