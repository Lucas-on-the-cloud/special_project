# Private processed-data handoff

This project keeps its reproducible code, manifests, metrics, and checkpoint
pointers in GitHub. Selected model weights are stored in the private Hugging
Face model repository `lucashwang0102/wgn-checkpoints`; processed dataset media is backed up in the
private Hugging Face dataset repository
`lucashwang0102/wgn-private-data`, accessible only to the authorized account.

## Backup status

The first complete backup finished and passed remote file verification on
20 October 2026. All 13 planned shards were uploaded: 510,774 files totaling
30.30 GiB. The remote repository contained all expected shards, manifests,
checksums, restore tooling, and verification tooling. This private Hugging Face
repository is the primary processed-data handoff for moving the experiments to
another machine; GitHub stores only the reproducible instructions and code.
Checkpoint restoration is documented separately in
[Private checkpoint handoff](private-checkpoint-handoff.md).

## Backed-up scope

The backup is generated from the locked manifests rather than by copying the
whole `C:/sp/data` directory. This avoids raw downloads, source ZIP files,
smoke-test data, caches, and frames unused by the experiments.

| Group | Locked manifest | Referenced files | Size |
|---|---|---:|---:|
| FaceForensics++ c23/c40 and FaceShifter | `FaceForensics++-official.json` | 180,000 | 11.76 GiB |
| Celeb-DF v2 DeepfakeBench RGB | `Celeb-DF-v2.json` | 16,420 | 0.92 GiB |
| Celeb-DF v2 official-direct | `Celeb-DF-v2-official-direct.json` | 16,576 | 0.91 GiB |
| DFDC | `DFDC.json` | 132,116 | 7.58 GiB |
| WildDeepfake | `WildDeepfake.json` | 165,662 | 9.13 GiB |
| **Total** | | **510,774** | **30.30 GiB** |

The uploader creates 3 GiB tar shards, records SHA-256 for each shard, uploads
one shard at a time, and deletes only the temporary local tar after the remote
commit succeeds. Its state in `C:/sp/data-handoff/upload-status.json` makes the
operation restartable.

## Authentication

Install the current CLI in a dedicated virtual environment and use device
login. Do not upgrade `huggingface_hub` inside the WGN training environment:
`timm==1.0.15` is paired with the `huggingface-hub==0.29.3` pin in the project
requirements. Never put a token in source files, shell history, logs,
documentation, or chat.

```powershell
C:\sp\.tools\py311\python.exe -m venv C:\sp\.tools\hf-cli
C:\sp\.tools\hf-cli\Scripts\python.exe -m pip install --upgrade huggingface_hub hf_xet
C:\sp\.tools\hf-cli\Scripts\hf.exe auth login
C:\sp\.tools\hf-cli\Scripts\hf.exe auth whoami
```

The repository must remain private. The uploader checks the remote `private`
flag before sending any data and stops if that check fails.

## Upload or resume

```powershell
$env:HF_HUB_DISABLE_XET = "1" # reliable HTTP fallback used by the watchdog
C:\sp\.tools\py311\python.exe `
  C:\sp\special_project\experiments\EXP-002-WGN\reproduction\code\backup_processed_data_to_hf.py `
  --repo-id lucashwang0102/wgn-private-data `
  --shard-gib 3
```

Re-running the command skips every shard already marked uploaded. The watchdog
script restarts an interrupted uploader automatically:

```powershell
C:\sp\.tools\py311\python.exe `
  C:\sp\special_project\experiments\EXP-002-WGN\reproduction\code\watch_private_data_backup.py
```

## Restore on another machine

After installing the dedicated Hugging Face CLI and completing device login,
download the private repository and run the included restore script:

```powershell
C:\sp\.tools\hf-cli\Scripts\hf.exe download lucashwang0102/wgn-private-data `
  --repo-type dataset `
  --local-dir C:\sp\data-handoff-download

powershell -ExecutionPolicy Bypass `
  -File C:\sp\data-handoff-download\restore.ps1 `
  -Destination C:\sp\data

C:\sp\.tools\py311\python.exe `
  C:\sp\data-handoff-download\verify_restored_data.py
```

`restore.ps1` verifies every tar shard against `SHA256SUMS.txt` before
extracting it. `verify_restored_data.py` then checks that every frame referenced
by the five locked manifests exists in the restored data root.

