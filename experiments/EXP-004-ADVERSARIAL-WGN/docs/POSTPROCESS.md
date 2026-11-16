# EXP-004 V3: paired, video and manipulation postprocessing

## Published summary tables

[Complete tables](../results/tables/COMPLETE-TABLES.md) combine all four full cohorts and all four methods. The initial 2,000-frame DFDC cohort remains historical evidence and is excluded from the full-cohort comparison. Markdown rounds presentation values; CSV retains source JSON float precision. `all-numeric-values.csv` exports every numeric/null/bool leaf through JSON pointers, and `PROVENANCE.json` hashes the generator, inputs and outputs.

Regenerate without GPU/data downloads:

```bash
python3 experiments/EXP-004-ADVERSARIAL-WGN/reporting/export_tables.py
python3 experiments/EXP-004-ADVERSARIAL-WGN/reporting/export_tables.py --check
```

The exporter checks cohort identities, counts, common settings, ASR numerators/denominators, summary/analysis agreement and finite quality counts before publishing tables. It reads only the committed compact JSON evidence. Raw per-frame logs and face examples remain outside Git.

Frames from the same source video are correlated. V3 records video, manipulation and source-cluster identities. Its final completion marker is `results.json` with `complete=true`.

After each successful run, execute:

```bash
python experiments/EXP-004-ADVERSARIAL-WGN/code/analyze_by_video.py \
  --run "$WGN_RUNTIME_ROOT/runs/final_ffpp_reconstruction_001" \
  --method jia-faa-reconstruction --bootstrap 1000
```

Repeat for `fgsm`, `pgd`, `frequency-init-control`, and for the DFDC run.

The output `jia-faa-reconstruction_video_analysis.json` contains:
- frame conditional Fake→Real ASR and percentile cluster-bootstrap 95% interval;
- conditional fake ASR per manipulation group (FF-DF, FF-F2F, FF-FS, FF-NT);
- video-level clean AUC and attacked-fake/clean-real AUC (mean frame scores per [manipulation, video, label]);
- video-level fake ASR on originally correctly classified fake videos.

FF++ bootstrap clusters use the official pair mapping, grouping the two real source IDs and all corresponding manipulation variants together (70 pairs on test). DFDC uses video IDs because original-source links are unavailable; its intervals remain exploratory. Video scores average only the selected frames; the 2,000-frame DFDC cohort does not imply complete-video evaluation.

After all eight analyses, export the compact evidence package:

```bash
python experiments/EXP-004-ADVERSARIAL-WGN/code/summarize_final.py \
  --runtime-root "$WGN_RUNTIME_ROOT" \
  --output experiments/EXP-004-ADVERSARIAL-WGN/results/initial-evaluation.json
```

This audits prelocked cohort/config fingerprints, paired clean scores, unchanged Real/false-negative images, final bounds and best-iterate selection. It reports quality on eligible Fake frames, band-wise statistics, a paired FAA/control flip table and cluster-bootstrap ASR difference. Runtime face examples and raw logs are not copied into Git.

For the subsequent full DFDC run, analyze all four methods in `final_dfdc_full_reconstruction_001`, then use `code/summarize_full_dfdc.py --runtime-root "$WGN_RUNTIME_ROOT" --output-dir experiments/EXP-004-ADVERSARIAL-WGN/results`. This generates the evidence JSON and a base report; the report also contains reviewed scientific interpretation and may include editorial annotations beyond the generated base. The original cohort outputs remain preserved.

Report both the numerator and denominator of conditional ASR. Do not claim WGN WGSA is a causal vulnerability solely from gate drift. Stronger attack restarts and matched, trained backbone ablations remain follow-up steps.

## Full Celeb-DF-v2 official-direct and WildDeepfake

`code/run_external_full.py --repo-root "$WGN_REPO_ROOT" --runtime-root "$WGN_RUNTIME_ROOT"` locks both full cohorts/configs, waits for checksum-verified restoration, runs each clean gate and all four attacks sequentially, analyzes each method with 1,000 bootstrap replicates, then calls `summarize_external_full.py`. It stops on any failed subprocess/gate and records the failed stage in `runtime/external-full-status.json`; it never overwrites an existing attack directory. Restoration can run concurrently with `restore_lab_data.py --runtime "$WGN_RUNTIME_ROOT" --datasets celebdf_official_direct wilddeepfake`.

Each full run is `runs/final_{celebdf,wilddeepfake}_full_reconstruction_001/`. Compact reports/evidence are `results/full-{celebdf,wilddeepfake}-{report.md,evaluation.json}`. The audit additionally checks unchanged core attack/quality/diagnostics hashes against the completed full DFDC run and checks every snapshotted Python hash. Video/sequence bootstrap intervals for both external datasets remain exploratory without shared source/identity linkage. WildDeepfake's 806 grouped records are face-sequence records, not 806 independently sourced original videos.

For manual postprocessing after four per-method analyses: `python code/summarize_external_full.py --runtime-root "$WGN_RUNTIME_ROOT" --dataset celebdf --output-dir results` (paths relative to EXP-004); repeat with `--dataset wilddeepfake`. No attack settings are selected by postprocessing.
