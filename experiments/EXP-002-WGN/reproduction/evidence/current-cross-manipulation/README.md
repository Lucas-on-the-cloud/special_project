# Current cross-manipulation status

Scheduled after the EXP-003 single-GPU queue. The resume-safe runner will smoke
test and independently train DF, F2F, FS, and NT for 25 epochs, then create the
complete 4 × 4 frame-AUC matrix here. It also preserves each `best.pt` and its
SHA-256 checksum under `../../artifacts/current-cross-manipulation/`.

The final report will compare three sources using the same Table 3 layout:

1. the WGN paper;
2. the archived RTX 5090 reproduction;
3. the active RTX 5060 Ti reproduction.

Runtime state and logs are written to
`C:/sp/runs/wgn_reproduction_current/`. The runner waits for EXP-003 to reach
`queue_complete`, so the two experiment tracks do not share the GPU.
