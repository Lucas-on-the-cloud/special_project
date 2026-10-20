# Private checkpoint handoff

All selected WGN `best.pt` files are stored in the private Hugging Face model
repository [`lucashwang0102/wgn-checkpoints`](https://huggingface.co/lucashwang0102/wgn-checkpoints).
GitHub stores the experiment record and an adjacent `CHECKPOINT.json` pointer;
it no longer stores the weight files themselves.

The authoritative machine-readable list of remote paths, direct URLs, sizes and
SHA-256 hashes is [`checkpoint-registry.json`](checkpoint-registry.json). Access
requires the authorized `lucashwang0102` Hugging Face account.

## Restore all checkpoints

```powershell
C:\sp\.tools\hf-cli\Scripts\hf.exe auth login
C:\sp\.tools\hf-cli\Scripts\hf.exe download lucashwang0102/wgn-checkpoints `
  --local-dir C:\sp\checkpoint-handoff
```

The download preserves the experiment directory layout. Copy only the selected
checkpoint needed for evaluation into the runtime directory expected by the
script. Verify it first with `Get-FileHash -Algorithm SHA256` against the
adjacent GitHub `CHECKPOINT.json` or the central registry.

## Current checkpoint links

| Experiment artifact | Private checkpoint |
|---|---|
| EXP-002 reproduced WGN reference | [baseline_final/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/best.pt) |
| EXP-002 cross-manipulation DF | [df/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/current-cross-manipulation/df/best.pt) |
| EXP-002 cross-manipulation F2F | [f2f/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/current-cross-manipulation/f2f/best.pt) |
| EXP-002 cross-manipulation FS | [fs/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/current-cross-manipulation/fs/best.pt) |
| EXP-002 cross-manipulation NT | [nt/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/current-cross-manipulation/nt/best.pt) |
| EXP-002 Table 1 FaceShifter c23 | [faceshifter_c23/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/current-table1/faceshifter_c23/best.pt) |
| EXP-002 Table 1 FaceShifter c40 | [faceshifter_c40/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/current-table1/faceshifter_c40/best.pt) |
| EXP-002 Table 1 FF++ c40 | [ffpp_c40/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-002-WGN/reproduction/artifacts/current-table1/ffpp_c40/best.pt) |
| EXP-003 gradient | [gradient_final/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/gradient_final/best.pt) |
| EXP-003 curriculum | [curriculum_final/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/curriculum_final/best.pt) |
| EXP-003 temporal consistency | [temporal_final/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/temporal_final/best.pt) |
| EXP-003 temporal control | [temporal_control_final/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/temporal_control_final/best.pt) |
| EXP-003 degradation consistency | [degradation_consistency_final/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/degradation_consistency_final/best.pt) |
| EXP-003 degradation control | [degradation_control_final/best.pt](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/degradation_control_final/best.pt) |

New final runs are added by the publisher. A publication is successful only
after Hugging Face hash verification and GitHub metadata verification both pass.
