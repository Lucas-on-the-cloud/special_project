# EXP-004 / EXP-005 research handoff

Updated 2026-11-16 after the user replaced the EXP-005 architecture draft with a second attack study and completed the evaluations.

- [EXP-004](../experiments/EXP-004-ADVERSARIAL-WGN/README.md): frozen WGN, Jia FAA reconstruction, FGSM/PGD and paired initialization control. All four full cohorts completed with audits; extension finished2026-11-16,02:31:12 Asia/Taipei. [Overview](../experiments/EXP-004-ADVERSARIAL-WGN/results/cross-dataset-overview.md). Its parameters/source snapshots stay fixed.
- [EXP-005](../experiments/EXP-005-STATATTACK-WGN/README.md): Hou2023 StatAttack/MStatAttack against the same frozen WGN/four full cohorts. Source-adapted40 profile, WGN feature adapter, reconstructed MStatAttack and two matched controls completed; all per-dataset audits passed. Results and five-method comparison are in the experiment README. [Plan](../experiments/EXP-005-STATATTACK-WGN/PLAN.md), [specification](../experiments/EXP-005-STATATTACK-WGN/docs/HOU-ALGORITHM-SPEC.md).
- [Five-method ASR comparison](../experiments/EXP-005-STATATTACK-WGN/results/five-method-comparison.md): shared full-cohort comparison for FGSM, PGD, Jia FAA, Hou StatAttack and reconstructed MStatAttack, including the non-matched-budget caveat.
- [Archived RCWG draft](archive/exp005-rcwg-draft/ARCHIVE-NOTE.md): original four files preserved byte-for-byte; `ARCHIVE.json` stores hashes. This is not the active EXP-005 architecture or training plan.

Both active studies are attack evaluations. Keep EXP-002 weights, threshold and clean inference pipeline frozen; EXP-003 candidate models are not substituted. No defense training or new architecture is scheduled. Run EXP-005 on the single GPU only after EXP-004 finishes and EXP-005 implementation/specification, clean gates and development benchmark pass.

Reuse read-only processed media/checkpoint, but keep runtime outputs, configs, source snapshots and reference-bank metadata separate. Report ASR numerator/eligible denominator, clean/attacked AUC, image quality, runtime and fidelity limits. Source-reference access, budget units and MMD batch grouping differ from Jia and must be explicit. Original paper tables are not directly reproduced by changing detector/datasets.

Preserve the project's artifact/checksum policy; raw media, weights and credentials stay outside Git. Publication includes source, compact audited metrics, validation/provenance and protocol documents only.
