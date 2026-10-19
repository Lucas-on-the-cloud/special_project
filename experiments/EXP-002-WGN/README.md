# EXP-002 — WGN reproduction

EXP-002 owns the independent reproduction of the WGN paper. Its current
RTX 5060 Ti checkpoint is the frozen reference used by EXP-003 improvement
comparisons.

- [`reproduction/CURRENT-REPRODUCTION-STATUS.md`](reproduction/CURRENT-REPRODUCTION-STATUS.md)
  is the authoritative status for the active reproduced checkpoint.
- [`reproduction/artifacts/baseline_final/`](reproduction/artifacts/baseline_final/)
  contains that checkpoint, configuration, training metrics, evaluations, and
  checksum.
- [`reproduction/RTX5090-HISTORICAL-REPRODUCTION.md`](reproduction/RTX5090-HISTORICAL-REPRODUCTION.md)
  archives results from the previous machine whose checkpoint was not retained.

The fresh cross-manipulation run is scheduled behind the active EXP-003
single-GPU queue. Historical cross-manipulation JSON from the RTX 5090 run is
kept for provenance and must not be presented as evaluation of the active run.
