# EXP-005 — StatAttack / MStatAttack against frozen WGN

**Status (2026-11-16, complete):** all four full cohorts have been evaluated by both attacks and both matched initialization controls; coverage, pairing, bounds, reference schedule, source snapshots and summary audits passed. All 49 combined CPU tests (12 EXP-005 plus 37 EXP-004 regression tests), four clean gates and actual-WGN CUDA smoke/benchmark passed. DFDC resumed from its committed SQLite state after a batch-shape score-check correction; a full eligible-Fake clean-class parity preflight found zero class changes. The 960-frame train-only Real bank remains checksum-verified. The user replaced the former RCWG defense draft with this study; [the original draft is archived](../../docs/archive/exp005-rcwg-draft/ARCHIVE-NOTE.md).

Apply Hou et al., CVPR2023, [Evading DeepFake Detectors via Adversarial Statistical Consistency](https://openaccess.thecvf.com/content/CVPR2023/papers/Hou_Evading_DeepFake_Detectors_via_Adversarial_Statistical_Consistency_CVPR_2023_paper.pdf) to the reproduced WGN. StatAttack optimizes exposure, blur and noise using real/fake feature-distribution alignment; MStatAttack learns mixtures of those operations and identity across multiple layers. This is an adaptation to WGN and its four evaluation datasets, not a rerun of all original paper tables.

| Full processed test cohort | Frames | Real | Fake |
|---|---:|---:|---:|
| FF++ c23 | 11,200 | 5,600 | 5,600 |
| DFDC | 132,116 | 63,265 | 68,851 |
| Celeb-DF-v2 official-direct | 16,576 | 5,696 | 10,880 |
| WildDeepfake | 165,662 | 58,659 | 107,003 |

Use the same frozen EXP-002 checkpoint, preprocessing, threshold0.5 and full cohort identities as EXP-004. Primary endpoint is Fake→Real ASR among clean-correct Fake; all Real and baseline false-negative Fake remain unchanged. A separate FF++ **train-only Real reference bank** supplies MMD targets and is not an attacked/evaluation cohort. Face crops suffice; original videos are not required for the input-level method.

- [Implementation and full-run plan](PLAN.md): stages, reference policy, controls, outputs and resource gates.
- [Paper/source audit](docs/HOU-PAPER-AUDIT.md): verified mechanisms, source discrepancies, missing MStatAttack code and fidelity limits.
- [Active protocol](docs/PROTOCOL.md), [executable algorithm specification](docs/HOU-ALGORITHM-SPEC.md) and [locked profile](code/configs/hou_source_adapted_40.json): source-adapted StatAttack40 / reconstructed MStatAttack3layers.
- [Verification gates](docs/TEST_PLAN.md): what must pass before the full runs.
- [Provenance](docs/SOURCE-PROVENANCE.json): reviewed source commit, file identities and paper checksum.

The reviewed repository is [tobuta/evadingfakedetector](https://github.com/tobuta/evadingfakedetector/tree/bd62d1f44cf822f665a192aa348925ec6c1fa033). It provides StatAttack; MStatAttack is absent from that tree and is reconstructed explicitly here. The EXP-004 legacy `statistical_proxy` is not used. Execution remains sequential on the single GPU.

## Full-cohort results

Conditional Fake→Real attack success rate (ASR) among clean-correct Fake; each attack used40 optimization updates and MStatAttack uses3 layers. The initialization controls measure changes caused by each method's initial transforms without optimization.

| Dataset | Eligible Fake | Stat init control | MStat init control | StatAttack | MStatAttack |
|---|---:|---:|---:|---:|---:|
| FF++ c23 | 5,333 | 0.11% | 0.17% | **92.86%** | **94.04%** |
| Celeb-DF-v2 official-direct | 8,278 | 0.01% | 0.06% | **92.61%** | **94.17%** |
| DFDC | 42,932 | 6.07% | 3.64% | **93.86%** | **95.21%** |
| WildDeepfake | 88,521 | 0.02% | 0.05% | **92.12%** | **94.35%** |

These are results for this named WGN adaptation, not exact reproduction of Hou et al.'s original tables. DFDC's initialization controls have nontrivial ASR, so interpret optimized ASR alongside controls and quality/cost metrics. The measurements do not establish a causal WGSA mechanism or equal-strength ranking against Jia/FGSM/PGD. Full per-dataset Markdown and JSON reports are available for [FF++](results/ffpp-report.md), [Celeb-DF](results/celebdf-report.md), [DFDC](results/dfdc-report.md) and [WildDeepfake](results/wilddeepfake-report.md).

The combined [five-method comparison](results/five-method-comparison.md) adds EXP-004's FGSM, PGD and Jia FAA results.

The [DFDC resume audit](results/dfdc-resume-audit.json) records the clean-score batch-shape preflight and narrow database/source migration provenance.

## Validation

The combined EXP-004/EXP-005 CPU suite passed **49 tests** (37 + 12); the recorded JUnit evidence is [cpu-tests.xml](validation/cpu-tests.xml). Re-run it from the repository root with:

```bash
python -m pytest experiments/EXP-004-ADVERSARIAL-WGN/tests experiments/EXP-005-STATATTACK-WGN/tests -q
```

The GPU run audits and clean-gate evidence are summarized above and in [the test plan](docs/TEST_PLAN.md).

## Runtime and provenance

Runtime: `/home/naeem/Downloads/s1123570_sp1/exp05-runtime`. The queue finished at `2026-11-16T11:50:47Z`; `queue-status.json` records all four datasets complete. Per-run `progress.json`, logs, SQLite states and full per-frame JSONL remain in that runtime directory outside Git. See runtime `README-LIVE.md` for the completion record.

Actual-WGN smoke used 120 validation Fake frames per method, batch 30, with frozen parameters/buffers and feature/classifier agreement verified. StatAttack40 took 15.325 seconds, peak allocation 5,875.1 MiB; MStatAttack3layers40 took 19.741 seconds, peak 7,871.9 MiB. These are software/VRAM benchmarks, not final-test ASR or whole-pipeline runtime estimates. Full clean results match the canonical EXP-004 values. The algorithm specification/profile remain frozen from pre-run setup; runtime files hold full traces and progress history.

The queue used the existing isolated inference environment without package changes. Degradation/MMD code uses the pinned PyTorch/NumPy stack. Readiness/config/spec/source/reference identities were checked before GPU use; the failed DFDC stage was resumed with a recorded narrow migration after the clean-class preflight. The exclusive queue lock prevented duplicate workers.

```bash
./exp04-runtime/venv/bin/python -u \
  special_project/experiments/EXP-005-STATATTACK-WGN/code/queue_exp05.py \
  --exp04 exp04-runtime --runtime exp05-runtime \
  --profile special_project/experiments/EXP-005-STATATTACK-WGN/code/configs/hou_source_adapted_40.json
```

The command above documents how the queue was launched; the completed queue must not be restarted unless a new, separately identified run is intended. The implementation saves metrics/trace transactions per completed batch in SQLite, exports full per-frame JSONL and runs integrity/statistical postprocessing per dataset. Compact, audited reports are committed in this experiment folder; runtime traces and media are not included in Git.
