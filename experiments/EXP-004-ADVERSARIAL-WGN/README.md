# EXP-004 — Paper-grounded adversarial challenge of reproduced WGN

EXP-004 is the adversarial-resilience branch that follows the completed **EXP-002 WGN independent reproduction**.

**Research dependency:** reproduce WGN first → challenge the frozen detector with prior-paper adversarial mechanisms → establish vulnerability/mechanism → only then design EXP-005 defense.

## Authoritative documents
- [Research context](docs/RESEARCH-CONTEXT.md) — why EXP-004 exists and how it leads to EXP-005.
- [Scientific protocol](docs/PROTOCOL.md) — paper provenance, dataset, threat model, algorithm deviations, metrics and full-run protocol.
- [Verification/test plan](docs/TEST_PLAN.md) — mandatory T0–T9 gates before lab/full evaluation.
- [Video/statistical postprocessing](docs/POSTPROCESS.md).

## Core attack methods
- FGSM — standard baseline, Jia et al. CVPR 2022 §3.1 Eq. (2); originally Goodfellow et al.
- PGD — standard iterative baseline, Jia §3.1 Eq. (3); originally Madry et al.
- `jia-faa-adapt` — explicit adaptation of Jia §3.2 Eqs. (4)–(7), Figure 2 and Algorithm 1.

The adaptation is **not an exact author reproduction** because the paper is insufficient to recover an executable dynamic fusion matrix `M`; our specific `M` and pixel-L∞ constraint are documented in PROTOCOL.md.

The legacy exploratory `dct_pgd`, `hybrid_pgd`, and `statistical_proxy` must **not** be reported as Jia Hybrid or Hou StatAttack/MStatAttack.

## Frozen victim and data
- Victim: EXP-002 `baseline_final/best.pt`.
- Checkpoint SHA256: `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`.
- Primary dataset: official FaceForensics++ c23 **test** split.
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

## EXP-005 gate
EXP-005 must not be justified merely because an attack can change logits. We first need reproducible evasion and evidence about the mechanism. A defense contribution later requires adaptive white-box evaluation, adversarial-training controls, generalization tests, ablations and cost analysis.
