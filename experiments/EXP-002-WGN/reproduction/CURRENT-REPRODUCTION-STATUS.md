# Current WGN reproduction status

**Machine:** NVIDIA RTX 5060 Ti 16 GB

**Date:** 19 October 2026

**Role:** frozen WGN reference for EXP-003 improvements

**Runtime run name:** `baseline_final`

This is a rerun of the independently reproduced WGN configuration from EXP-002.
It was required because the checkpoint from the earlier RTX 5090 reproduction
was not saved. The word `baseline` in runtime files refers to this reproduced
WGN reference; it is not a separate method proposed by EXP-003.

## Completed

| Evaluation | AUC |
|---|---:|
| FF++ c23, frame | 98.21% |
| Celeb-DF v2 official-direct, video | 70.14% |
| DFDC, video | 69.67% |
| WildDeepfake, video | 71.54% |

- Best epoch: 20
- Checkpoint: [`artifacts/baseline_final/best.pt`](artifacts/baseline_final/best.pt)
- SHA-256: `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`

## Pending

- Table 3 cross-manipulation training and the 4 × 4 DF/F2F/FS/NT evaluation
  matrix for this exact protocol generation is running. It preserves all four
  independently trained checkpoints and creates a Paper/RTX 5090/RTX 5060 Ti
  comparison.
- Table 1 still needs three independently trained models: FF++ c40,
  FaceShifter c23, and FaceShifter c40. They are queued immediately after
  Table 3 with smoke tests, resume checkpoints, SHA-256 files, and GitHub
  publication. The existing c40/FaceShifter values from `baseline_final` are
  held-out evaluations of the c23 model and are not Table 1 reproduction rows.
- A final three-table report will be written to
  `CURRENT-FULL-REPRODUCTION.md` after those runs complete.

The directory
[`evidence/rtx5090-historical-cross-manipulation/`](evidence/rtx5090-historical-cross-manipulation/)
belongs to the earlier machine and does not close the pending item above.
