# EXP-004 — Paper-grounded adversarial challenge of reproduced WGN

EXP-004 is the adversarial-resilience branch that follows the completed **EXP-002 WGN independent reproduction**.

**Research scope:** reproduced WGN → Jia frequency-domain attacks with FGSM/PGD controls → measure evasion and analyze WGN mechanism. Other attack families and future defense design are separate studies; they do not change this experiment's locked methods, metrics or interpretation.

**Initial evaluation completed (2026-11-15):** FAA reconstruction flipped 2,731/5,333 eligible Fake frames on FF++ c23 (**51.21%**) and 506/606 on the locked 2,000-frame DFDC cohort (**83.50%**). Paired no-gradient controls achieved 6.08% and 23.60%. [Full report and compact evidence](results/INITIAL-EVALUATION-REPORT.md) include quality, uncertainty, manipulation/video analysis and claim limits. This does not establish original-author reproduction or a causal WGSA weakness.

**Full DFDC extension completed (2026-11-15):** all 132,116 restored test frames evaluated with unchanged attack settings. FAA flipped **36,072/42,932 eligible Fake frames (84.02%)**, versus **22.40%** for paired initialization control. The video-cluster bootstrap interval is 82.47–85.56% (exploratory source linkage). Clean continuity and post-run audits passed. [Full DFDC report](results/full-dfdc-report.md) and [evidence](results/full-dfdc-evaluation.json) supersede the 2,000-frame cohort as the coverage result; the initial run is preserved.

## Authoritative documents

**All four full test cohorts completed:** the extension finished 2026-11-16, 02:31:12 Asia/Taipei, including analyses and all audits. Celeb-DF-v2 official-direct: FAA **7,946/8,278 eligible Fake (95.99%)**, control 18.34%; WildDeepfake: **82,059/88,521 (92.70%)**, control 22.91%. Checkpoint, core attack/quality/diagnostics and settings match full DFDC.

- [Four-dataset overview](results/cross-dataset-overview.md).
- [Complete tables: all 16 dataset × method combinations](results/tables/COMPLETE-TABLES.md), with full-precision CSV for cohorts, methods, video/sequence results, manipulation groups, paired controls, mechanism outcomes and Haar bands.
- [Table input/output checksums](results/tables/PROVENANCE.json) and [deterministic exporter](reporting/export_tables.py).
- [Celeb-DF-v2 report](results/full-celebdf-report.md), [WildDeepfake report](results/full-wilddeepfake-report.md).

- [Lab status](docs/LAB-STATUS.md) — environment, restored data, clean gates and evaluation progress.
- [Execution plan](PLAN.md) — staged plan and current progress.
- [Active V3 protocol](docs/V3-PROTOCOL.md) — executable reconstruction, controls and locked FF++/DFDC schedule.
- [Jia algorithm specification](docs/JIA-ALGORITHM-SPEC.md) — paper-to-code mapping and unresolved fidelity details.
- [Isolated lab environment](docs/LAB-SETUP.md) — inference/test dependency pins and setup commands.
- [Research context](docs/RESEARCH-CONTEXT.md) — EXP-004 questions, evidence requirements and claim boundaries.
- [Archived V2 protocol](docs/PROTOCOL.md) — provenance of the earlier pixel-constrained adaptation.
- [Verification/test plan](docs/TEST_PLAN.md) — software, continuity and evaluation gates.
- [Video/statistical postprocessing](docs/POSTPROCESS.md).

## Core attack methods
- FGSM — standard baseline, Jia et al. CVPR 2022 §3.1 Eq. (2); originally Goodfellow et al.
- PGD — standard iterative baseline, Jia §3.1 Eq. (3); originally Madry et al.
- `frequency-init-control` — paired M/U(0,1)/feasibility without optimization.
- `jia-faa-reconstruction` — active V3 reconstruction of Jia §3.2 Eqs. (4)–(7), Figure 2 and Algorithm 1, with an explicit frequency-domain constraint.

The reconstruction is **not an exact author reproduction**: M, norm/budget and RGB feasibility are declared project choices in V3-PROTOCOL.md. The old `jia-faa-adapt` remains archived with its pixel-L∞ constraint. Pixel and frequency budgets are different units and do not establish matched attack strength.

The legacy exploratory `dct_pgd`, `hybrid_pgd`, and `statistical_proxy` must **not** be reported as Jia Hybrid or Hou StatAttack/MStatAttack.

## Frozen victim and data
- Victim: EXP-002 `baseline_final/best.pt`.
- Checkpoint SHA256: `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`.
- Primary dataset: official FaceForensics++ c23 **test** split.
- Cross-dataset evaluation: full DFDC test (132,116 frames), Celeb-DF-v2 official-direct (16,576) and WildDeepfake (165,662); initial 1,000 Fake + 1,000 Real DFDC cohort preserved separately. Seed 1024; clean continuity checks cover each full cohort.
- Processing: exactly the EXP-002 MTCNN face-crop/256×256 manifest pipeline.
- Real=0, Fake=1, threshold=0.5.
- Primary attack scope: Fake inputs; Real inputs remain unchanged.
- Primary endpoint: Fake→Real ASR conditional on the Fake being correctly detected before attack.

## Mandatory lab sequence

```bash
cd /lab/special_project
git pull origin main

export WGN_REPO_ROOT="$PWD"
export WGN_DATA_ROOT="/lab/data"
export WGN_CHECKPOINT="/lab/checkpoints/experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/best.pt"

bash experiments/EXP-004-ADVERSARIAL-WGN/run_lab_linux.sh
```

The script:
1. runs environment/artifact preflight;
2. runs all unit tests;
3. reproduces clean FF++ c23 metrics and **stops if they do not match EXP-002**;
4. runs only a 40-frame adversarial GPU smoke test.

The pilot is not publishable evidence. Read TEST_PLAN.md T5 before a full run.

## Current endpoint
Produce a reproducible assessment of whether frequency-domain attacks can fool WGN, together with evidence about affected subband statistics, gates and attention. Other attack families and architecture design are later studies based on evidence; they are not inputs to this experiment.
