# Experiment backup and machine handoff

This policy preserves each experiment across machine changes. GitHub stores the
research record; the private Hugging Face model repository stores selected
weights.

## Storage locations

| Content | Storage |
|---|---|
| Code, plans, configs, splits, metrics, logs and manifests | GitHub `main` |
| Selected final `best.pt` files | Private model repo [`lucashwang0102/wgn-checkpoints`](https://huggingface.co/lucashwang0102/wgn-checkpoints) |
| Processed dataset shards | Private dataset repo [`lucashwang0102/wgn-private-data`](https://huggingface.co/datasets/lucashwang0102/wgn-private-data) |
| Active-run `last.pt` with optimizer and RNG state | Local; upload privately only when a run must move |
| Tokens, signed URLs and approval records | Secure storage outside both repositories |

The model and dataset repositories must remain private. Do not put access tokens
in source, commands, logs, or documentation.

## Completion rule

A final run is complete only when:

1. its hypothesis, code commit, resolved config, dataset manifest and seed are recorded;
2. training metrics and locked evaluation results are saved;
3. `best.pt` has been uploaded to the private model repository;
4. the remote LFS SHA-256 matches the local file;
5. GitHub contains `CHECKPOINT.json`, `ARTIFACT-MANIFEST.json`, checksums and logs;
6. the metadata commit is pushed and verified on `main`.

Finishing the final epoch locally does not satisfy this rule.

## Required artifact directory

```text
experiments/EXP-XXX/artifacts/<run-name>/
├── README.md
├── CHECKPOINT.json
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

`CHECKPOINT.json` is the versioned pointer to `best.pt`. It records the private
repository, remote path, browser and download URLs, byte count, upload time and
SHA-256. `ARTIFACT-MANIFEST.json` repeats the checkpoint identity alongside the
run metadata. `SHA256SUMS.txt` covers the small files committed to GitHub.

Method-specific records such as curriculum difficulty caches and
cross-manipulation results must also be included when they affect interpretation
or avoid repeating an expensive step.

## Before, during and after training

Before training, freeze the comparison protocol, commit the source/configuration,
validate the dataset manifest and pass a real-data CUDA smoke test. During
training, write metrics and `last.pt` atomically, maintain a status file and use
a resume-safe watchdog.

After a final run:

1. Select `best.pt` by the declared validation metric.
2. Run the common locked evaluation suite.
3. Upload `best.pt` to the private Hugging Face model repo.
4. Verify its remote SHA-256 before deleting any Git-tracked copy.
5. Write the pointer, artifact manifest, checksums and experiment registry.
6. Commit and push the small research record to GitHub `main`.
7. Verify the remote Git commit.

The repository-wide machine-readable index is
[`checkpoint-registry.json`](checkpoint-registry.json). The human restore guide
and direct checkpoint links are in
[`private-checkpoint-handoff.md`](private-checkpoint-handoff.md).

## Restore on another machine

Authenticate with Hugging Face using device login. Use a separate CLI
environment so the pinned WGN training environment stays unchanged:

```powershell
C:\sp\.tools\py311\python.exe -m venv C:\sp\.tools\hf-cli
C:\sp\.tools\hf-cli\Scripts\python.exe -m pip install --upgrade huggingface_hub hf_xet
C:\sp\.tools\hf-cli\Scripts\hf.exe auth login
```

Download a checkpoint using the path from its `CHECKPOINT.json`:

```powershell
C:\sp\.tools\hf-cli\Scripts\hf.exe download lucashwang0102/wgn-checkpoints `
  experiments/EXP-003-IMPROVEMENT-WGN/artifacts/degradation_control_final/best.pt `
  --local-dir C:\sp\checkpoint-handoff

Get-FileHash `
  C:\sp\checkpoint-handoff\experiments\EXP-003-IMPROVEMENT-WGN\artifacts\degradation_control_final\best.pt `
  -Algorithm SHA256
```

Compare the digest with `CHECKPOINT.json`, restore processed data using
[`private-processed-data-handoff.md`](private-processed-data-handoff.md), then
run smoke inference before a full evaluation.

## EXP-003 automation

[`publish.py`](../experiments/EXP-003-IMPROVEMENT-WGN/code/publish.py) performs
the final-run flow automatically: upload and verify the checkpoint, write the
pointer and metadata, update the results/registries, then commit and verify the
GitHub record. Existing selected checkpoints can be uploaded with
[`sync_checkpoints_to_hf.py`](../experiments/EXP-003-IMPROVEMENT-WGN/code/sync_checkpoints_to_hf.py).

New degradation runs in the active queue use this publication path when each
run finishes.
