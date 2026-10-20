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

## Cross-manipulation completed

- Current RTX 5060 Ti all-cell mean AUC: **71.29%**
- Current RTX 5060 Ti unseen-only mean AUC: **62.00%**
- Four independently trained checkpoints: `artifacts/current-cross-manipulation/`
- Full comparison: `evidence/current-cross-manipulation/RESULTS.md`

The directory
[`evidence/rtx5090-historical-cross-manipulation/`](evidence/rtx5090-historical-cross-manipulation/)
belongs to the earlier machine and does not close the pending item above.
