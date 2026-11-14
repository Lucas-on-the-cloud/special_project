# EXP-004 — Paper-attributed adversarial evaluation of frozen WGN

**Active protocol: V2** — [docs/PROTOCOL.md](docs/PROTOCOL.md) is the authoritative scientific and lab reproducibility document. **Status:** CPU unit tests can be run; real GPU experiment is pending.

## Paper grounding

1. **FGSM and PGD** — Jia et al. CVPR 2022 §3.1 Eqs. (2)–(3), with original adversarial baselines from Goodfellow 2015 / Madry 2018.
2. **Jia Frequency Adversarial Attack adaptation** — Jia et al. CVPR 2022 §3.2 Eqs. (4)–(7), Figure 2, Algorithm 1. We preserve block DCT → frequency fusion matrix → gradient optimization → IDCT; but use a specifically documented surrogate fusion M and a pixel-L∞ constraint. This is **NOT an exact author reproduction**.
3. **Hou StatAttack/MStatAttack** are **NOT yet implemented**. The previous `statistical_proxy` is a heuristic, not their algorithm.
4. **Jia hybrid Algorithm 2** is **NOT yet implemented**. The previous `hybrid_pgd` is not their method.

**Do not use the old `code/run_exp04.py` to report paper-method results.** It remains only as a legacy exploratory probe for traceability. The lab script now invokes **`code/run_exp04_v2.py`** and **`code/paper_aligned_attacks.py`**.

## Data and checkpoint
- Frozen independent EXP-002 reference, strict model state_dict.
- Official FF++ `test` split, MTCNN-cropped 256×256 PNG faces from the EXP-002 manifest.
- C23 primary; C40 supplementary under identical c23 checkpoint.
- Real=0, Fake=1. Attack **fake frames only**; keep Real inputs untouched for AUC reference.
- Exact checkpoint SHA256 is checked by default. Private data are restored from the repository's authorized private Hugging Face handoff; checkpoints from the public handoff.

## Run

```bash
cd /lab/special_project
git pull origin main
export WGN_REPO_ROOT="$PWD"
export WGN_DATA_ROOT="/lab/data"
export WGN_CHECKPOINT="/lab/ckpt/experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/best.pt"
bash experiments/EXP-004-ADVERSARIAL-WGN/run_lab_linux.sh
```

The 40-frame run is for smoke testing only. Exact full-run CLI, arguments, metric definitions, source links, provenance, experiment gating and known deviations are in [PROTOCOL.md](docs/PROTOCOL.md).

**Primary endpoint**: fake-to-real ASR conditional on the clean fake being correctly classified at threshold 0.5. **Secondary**: AUC with Real clean and Fake attacked, plus WGSA statistics/gates/attention shifts. Neither is proof of causal WGSA failure without trained control models.

### Important
EXP-004 does not train or mutate the original model; EXP-005 should proceed only if this experiment reveals a meaningful, reproducible vulnerability and the mechanism controls support it.
