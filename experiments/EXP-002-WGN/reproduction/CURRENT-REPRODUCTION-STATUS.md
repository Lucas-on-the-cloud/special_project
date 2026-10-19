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

- Cross-manipulation training and the 4 × 4 DF/F2F/FS/NT evaluation matrix for
  this exact protocol generation. It is queued after EXP-003 and will preserve
  all four best checkpoints plus a Paper/RTX 5090/RTX 5060 Ti comparison table.
- Final FF++ c40 and FaceShifter c23/c40 evaluation in the current queue sweep.

The directory
[`evidence/rtx5090-historical-cross-manipulation/`](evidence/rtx5090-historical-cross-manipulation/)
belongs to the earlier machine and does not close the pending item above.
