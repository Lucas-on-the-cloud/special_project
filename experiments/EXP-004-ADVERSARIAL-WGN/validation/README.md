# EXP-004 publication validation

The published record covers four full processed test cohorts (325,554 frames), four methods and a frozen EXP-002 checkpoint. No new detector was trained. The checkpoint pointer reuses the existing public Hugging Face artifact; weights and processed media are not stored in Git.

- `cpu-tests.xml`: 37 EXP-004 CPU tests passed on the publication candidate.
- `ARTIFACT-MANIFEST.json`: full-cohort identities, evidence links, common core-source checks and publication-file hashes.
- `SHA256SUMS.txt`: experiment-relative hashes for publication files, including the manifest (excluding only this checksum file itself).
- `../results/tables/PROVENANCE.json`: deterministic table generator/input/output hashes. All source numeric/null/bool values are exported without rounding to CSV.

From repository root:

```bash
python -m pytest experiments/EXP-004-ADVERSARIAL-WGN/tests -q
python3 experiments/EXP-004-ADVERSARIAL-WGN/reporting/export_tables.py --check
cd experiments/EXP-004-ADVERSARIAL-WGN
sha256sum --check validation/SHA256SUMS.txt
```

CUDA clean gates and completed attack audits were recorded during the original runs; they are not re-executed by the CPU publication check. The compact evidence preserves all original run source hashes. Core attack/quality/diagnostic code matches every full run; dataset adapters/CLI gained external-dataset support between runs. Original per-frame logs, source snapshots and examples remain in the lab runtime outside Git.

FAA is an explicitly specified Jia reconstruction, not author-verified exact reproduction. Pixel and DCT budgets have different units. ASR conditions on clean-correct Fake; Real and baseline Fake false negatives stay unchanged. External video/sequence intervals are exploratory without original-source linkage. Diagnostics do not establish causal WGSA weakness.
