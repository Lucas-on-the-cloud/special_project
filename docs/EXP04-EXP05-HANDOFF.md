# EXP-004 / EXP-005 research handoff
EXP-004 contains a frozen-checkpoint WGN adversarial evaluator and WGSA diagnostics.
EXP-005 contains a reliability-calibrated WGSA candidate (not yet trained/validated).
Both experiments are isolated from EXP-002 and EXP-003; no baseline files changed.

Coding workflow: Explore → Plan → Code → Verify → Review → Commit, as described in 06_Vibe_coding.pdf. Preserve the repository's GitHub/Hugging Face backup and checksum policy. Do not commit processed data, checkpoints or credentials. Start with CPU tests and the small Linux pilot, and only then run a full evaluation. See each experiment README.
