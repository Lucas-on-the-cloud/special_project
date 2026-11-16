# EXP-005 validation evidence

`cpu-tests.xml` records the combined 49-test run (37 EXP-004 regression tests and12 EXP-005 tests), all passing after the reviewed runner score-parity correction. Re-run from the repository root with the project's experiment environment:

```bash
python -m pytest experiments/EXP-004-ADVERSARIAL-WGN/tests experiments/EXP-005-STATATTACK-WGN/tests -q
```

The CPU suite validates independent MMD/blur calculations, gradients and bounds, method composition, reference cycling, frozen-model behavior and transactional resume logic. The full-cohort GPU gates, smoke, runs and per-dataset audits are documented in the [experiment plan](../PLAN.md), [test plan](../docs/TEST_PLAN.md) and compact result JSON files. Full runtime JSONL, SQLite, face crops, images and model weights are excluded from Git.
