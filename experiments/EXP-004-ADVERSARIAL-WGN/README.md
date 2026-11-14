# EXP-004 — Adversarial vulnerability of frozen WGN

**Status:** CPU unit tests available; GPU/real-data evaluation pending. The experiment does not train or modify EXP-002.

## Research questions
- RQ1: Can small frequency-domain adversarial perturbations misclassify fake images as real?
- RQ2: How do subband statistics, gating weights, and attention maps change?
- RQ3 is reserved for EXP-005; a defense is not assumed necessary until demonstrated.

## Threat model
White-box, untargeted, image-space L-infinity bounded perturbations, default epsilon 4/255 on RGB in [0,1]. FGSM, pixel PGD, block-DCT low/mid/high/all, pixel-DCT hybrid and an exposure/blur/noise statistical proxy are included.

**These are research probes, not exact reproductions** of Jia et al. (CVPR 2022) or Hou et al. (CVPR 2023). The Jia hybrid is meta-learning-based in the original paper; our hybrid alternates gradients. Pixel projection after inverse DCT may create out-of-band energy.

## Integration
Uses EXP-002 WGN source and the frozen reproduced checkpoint with strict state-dict loading. Uses original FF++ official manifest and deterministic test preprocessing. Never stores data or weights in Git.

## Linux lab pilot

```bash
git clone https://github.com/Lucas-on-the-cloud/special_project.git
cd special_project
# Activate existing WGN-compatible Python environment (torch, torchvision, timm,
# Pillow, scikit-learn, numpy, PyYAML and pytest).
export WGN_REPO_ROOT="$PWD"
export WGN_DATA_ROOT="/lab/path/to/data"
export WGN_CHECKPOINT="/lab/path/to/baseline_final/best.pt"
bash experiments/EXP-004-ADVERSARIAL-WGN/run_lab_linux.sh
```

Expected frozen checkpoint SHA256:
`a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`.

Restore via `docs/checkpoint-handoff.md`. Restore processed data privately via `docs/private-processed-data-handoff.md`; no tokens/secrets in Git. Existing Windows-style relative manifest paths are supported by EXP-002 loader, but absolute roots must be Linux paths.

## Windows pilot (existing C:/sp layout)
```powershell
python -m pytest experiments/EXP-004-ADVERSARIAL-WGN/tests -q
python experiments/EXP-004-ADVERSARIAL-WGN/code/run_exp04.py `
  --repo-root C:/sp/special_project `
  --checkpoint C:/sp/checkpoint-handoff/experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/best.pt `
  --manifest C:/sp/data/FaceForensics++-official.json `
  --data-root C:/sp/data `
  --expected-sha256 a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6 `
  --output C:/sp/exp04_runs/pilot_seed1024 `
  --max-samples 40 --batch-size 4 --steps 3
```

After the smoke test succeeds, run a full test in a **new** output directory, omit `--max-samples`, and use `--steps 10` or more. Do not use held-out test sets for defense tuning.

## Artifacts and interpretation
`environment.json`: checkpoint/manifest SHA256, CUDA and attack settings.
`results.json`: attacked and same-sample clean AUC, attacked accuracy, fake-to-real ASR conditioned on correctly detected fake inputs, pixel L-infinity, WGSA statistic/gate/attention drift.

This implementation attacks **all** input labels. AUC is calculated over attacked real and fake images; fake-evasion ASR uses only initially correct fake predictions. To establish causality, add matched backbone-only and controlled-WGSA ablations. Attack failure is not a robustness guarantee; evaluate multiple restarts and adaptive attacks later. Video-level uncertainty must account for correlated frames.
