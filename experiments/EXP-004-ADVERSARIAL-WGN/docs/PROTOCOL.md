# EXP-004 V2 — Paper-attributed adversarial vulnerability protocol

**Project**: WGN adversarial resilience (2026-11-14). **Research stage**: RQ1 vulnerability / RQ2 mechanism only. **Status**: implementation and CPU test; no laboratory CUDA evaluation results have been claimed. **Baseline**: EXP-002 frozen independent reproduction, not the WGN authors' official source. **Scope**: reproducible, white-box, fake-to-real evasion of a frozen frame classifier.

## 1. Research questions and falsifiable hypotheses

- **RQ1**: Can small, input-space frequency-domain perturbations cause a pretrained WGN to misclassify genuine *fake-labeled face crops* as real?
- **RQ2**: During a successful attack, are the changes to the Haar subband statistics, 4 learned gates and IDWT attention larger than for unsuccessful attacks? Is this behavior specific to WGSA rather than the MobileViT backbone?
- **H1 (to test)**: Frequency-domain attacks cause nontrivial fake-to-real evasion under specified constraints.
- **H2 (to test)**: WGSA internal changes correlate with evasion; *correlation is not proof of causality*.
- **H3 (future control)**: Matched, trained backbone-only or neutral-gate variants differ in vulnerability from WGN. A newly initialized backbone-only classifier is not a valid matched control.

Do not call EXP-004 a defense experiment; EXP-005 is separate and conditional on these findings.

## 2. Exactly which papers supply the algorithms?

| Implementation | Grounding | Source section / equation | What was faithfully retained? | What differs? |
|---|---|---|---|---|
| `fgsm` | Goodfellow et al., ICLR 2015; reproduced as baseline in Jia et al., CVPR 2022 | Jia §3.1 Eq. (2) | Gradient sign update on RGB under pixel norm bound | We evaluate specifically Fake→Real; epsilon declared on RGB [0,1] |
| `pgd` | Madry et al., ICLR 2018; baseline described by Jia et al. | Jia §3.1 Eq. (3) | Repeated gradient-sign pixel steps and L∞ projection | Default no random start for comparability; vary restart settings later |
| `jia-faa-adapt` | Jia et al., *Exploring Frequency Adversarial Attacks for Face Forgery Detection*, CVPR 2022 | §3.2 Eq. (4)–(7), Figure 2, Algorithm 1 | K×K block DCT, frequency mask/fusion matrix M, optimized perturbation P via adversarial gradient, IDCT and repeat | **NOT an exact reproduction:** precise dynamic M is not executable from paper text; we explicitly choose an energy-proportional M from clean DCT, and use pixel-space L∞ rather than paper Eq. (4)'s frequency-space constraint |

**References**:
1. [Jia et al. (CVPR 2022), official paper](https://openaccess.thecvf.com/content/CVPR2022/html/Jia_Exploring_Frequency_Adversarial_Attacks_for_Face_Forgery_Detection_CVPR_2022_paper.html)
2. [Goodfellow et al. (ICLR 2015), Explaining and Harnessing Adversarial Examples](https://arxiv.org/abs/1412.6572)
3. [Madry et al. (ICLR 2018), Towards Deep Learning Models Resistant to Adversarial Attacks](https://arxiv.org/abs/1706.06083)
4. [Hou et al. (CVPR 2023), StatAttack / MStatAttack](https://openaccess.thecvf.com/content/CVPR2023/html/Hou_Evading_DeepFake_Detectors_via_Adversarial_Statistical_Consistency_CVPR_2023_paper.html) — **NOT implemented as a verified paper method in V2**.

**Methodological boundary:** The legacy `code/attacks.py` exposes extra DCT band probes, `hybrid_pgd`, and `statistical_proxy`. They were not exact reproductions and **MUST NOT** be used for core paper-based attack claims. The V2 runner imports only `code/paper_aligned_attacks.py`. Jia Algorithm 2 uses alternating *full* spatial/frequency attack stages and shared clipping, not merely alternate sign-gradient domains; do not call legacy `hybrid_pgd` Jia Hybrid. Hou uses distribution-aware statistical consistency objectives and an optimized multi-layer transformation; legacy `statistical_proxy` omits both, so it must not be called StatAttack.

### Jia frequency adaptation, explicit implementation

For RGB crop `x` in `[0,1]^(3×256×256)`, divide into 8×8 blocks and compute orthonormal 2-D DCT: `C=DCT_8(x)`.

We operationalize the paper's adaptive fusion matrix by:
1. Calculate `a[c,u,v]`: mean over all spatial blocks of `abs(C[c,u,v])`.
2. Normalize per channel by `max_(u,v) a[c,u,v] + 1e-8`.
3. Define `M[c,u,v] = m_floor + (1-m_floor) × normalized_a[c,u,v]` and tile M across all blocks.
4. Initialize `P ~ U(0,alpha)` (our declared small initialization, distinct from Jia's `U(0,1)`).
5. At each step, form `IDCT(DCT(x_adv)+M ⊙ P)`; apply pixel projection and calculate BCE gradient w.r.t. P, then update `P←P+alpha×sign(∇_P BCE)`; reconstruct and clamp.
6. After the last iteration, evaluate the final RGB image.

This preserves **the transformation/fusion/gradient structure** of Jia §3.2 but not the exact original optimization or dynamically reset M. It is labeled **Jia-FAA adaptation** everywhere. The high/mid/low spectrum ablations in the legacy module remain exploratory and are not attached to a paper's official claim.

We impose a uniform pixel-domain budget for comparability:

`x_adv = clamp_[0,1](clip_[x−eps,x+eps](candidate))`.

This is **different from Jia Eq. (4)**, which constrains a difference in the DCT domain. Projection can also move energy between frequencies. Report *pixel-L∞-bounded Jia-inspired attack*, not strict frequency-only perturbation or original Jia attack ASR.

## 3. Dataset provenance, preparation and split lock

The baseline data and preprocessing must **not** be re-created from scratch.

| Dimension | EXP-002 frozen reference |
|---|---|
| Dataset | Official FaceForensics++ (FF++) |
| Sources | FF-real and FF-DF, FF-F2F, FF-FS, FF-NT; FaceShifter is a separate evaluation |
| Compression | C23 primary; C40 supplementary, using the **same c23-trained checkpoint** for cross-compression test |
| Split | Official video-disjoint `splits/train.json`, `val.json`, `test.json`; EXP-004 uses only `test` |
| Processing | EXP-002 `preprocess_ffpp_official.py`: evenly sampled video frames, MTCNN face crop, resize to 256×256, stored as RGB-compatible PNG files |
| Number sampled | 40 frames per real video, 10 frames per fake video per manipulation |
| Inference transforms | PIL open → RGB → Resize(256×256) → ToTensor(). **No test augmentation / no ImageNet normalization** |
| Manifest | `FaceForensics++-official.json` with video IDs, manipulation keys, relative frame paths, compression, split |
| Labels | Real=0; Fake=1; fake score = sigmoid(WGN logit), threshold 0.5 |
| Main reference | `experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/CHECKPOINT.json` |

EXP-002's independent FF++ c23 model has **frame AUC 98.21%** and **frame ACC 93.92%** in its paper-aligned in-domain evaluation. The same c23 checkpoint has a separate C40 cross-compression evaluation; **do not mix** this with the separately trained C40 Table-1 checkpoint (reported AUC 87.80%). EXP-003 compared gradient, curriculum and temporal strategies with this same reference, and uses held-out datasets for generalization. EXP-004 must not modify these frozen artifacts.

**Checkpoint**: public Hugging Face `lucashwang0102/wgn-checkpoints`, `experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/best.pt`; required SHA256
`a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`.
**Data**: authorized processed data from the *private* `lucashwang0102/wgn-private-data` dataset repository; refer to `docs/private-processed-data-handoff.md`. Keep credentials outside scripts/logs/Git.

### Pilot versus full population

The reproducible 40-frame pilot uses only **official test** records and deterministically distributes samples across Real/Fake, manipulation groups and videos. It is a **smoke test, not statistically meaningful**. Full evaluation uses the entire locked FF++ test manifest and all scheduled fake videos. Never use test-set results to select attack or defense hyperparameters. If attack settings need tuning, use a disjoint development/validation subset and lock settings before final test.

## 4. Threat model and explicit adversarial objective

- **Victim**: frozen, independently reproduced WGN (MobileViT-S → WGSA → fusion → classifier).
- **Attacker knowledge**: full weights/gradients (white-box).
- **Attacker input**: already cropped 256×256 RGB tensors; does not control the physical camera, MTCNN preprocessing or image decoding.
- **Adversary goal**: transform fake-labeled inputs to receive **Real** prediction.
- **Attack optimization**: maximize `BCEWithLogits(f(x_adv), y=1)` for fake images only.
- **Budget**: default RGB pixel `L∞ ε=4/255`; report tests at `2/255`, `4/255`, `8/255` as distinct settings if compute allows. `alpha=1/255`, `N=10` steps as a pilot starting point **not Jia official parameter reproduction**.
- **Constraint validation**: all outputs in [0,1] and `||x_adv-x||_∞≤ε+1e-6`.
- **Control real samples**: untouched. No synthetic adversarial perturbation on Real inputs for the primary fake-evasion metric.
- **Threshold**: fake if `sigmoid(logit)≥0.5`; freeze threshold before seeing attacks.
- **No training**: the model is always `eval()`, gradients to image but not parameters.
- **Additional attacks**: stronger random-restart PGD and transfer attacks reserved for follow-up; **failure of this first attack does not certify robustness**.

## 5. What counts as successful fooling?

Let `s(x)=sigmoid(f_WGN(x))` be Fake probability with threshold `τ=0.5`.

For image `i`, clean success is `y_i=1 and s(x_i)≥τ`; adversarial evasion is `s(x_adv_i)<τ`.

**Primary metric — conditional Fake→Real ASR:**

`ASR = #(fake, clean_correct, attacked_pred_real) / #(fake, clean_correct)`.

Only originally correctly detected fake frames enter the denominator. If no eligible frames, ASR = null, never 0%.

**Secondary metrics:**
- **Unconditional fake evasion**: fraction of all fake frames classified Real after attacks, including baseline errors.
- **Attacked-fake / clean-real AUC**: all Real scores are unchanged, Fake scores come from attacked fakes. This is **not general untargeted robust AUC** over adversarially attacked both classes.
- **Clean reference AUC/ACC**: recomputed on exactly the *same selected records*.
- **Magnitude**: max and mean L∞ per image, sanity threshold.
- **Per manipulation**: DF / F2F / FS / NT; do not collapse away failure modes.
- **Video-level analysis (planned)**: aggregate mean fake scores per video and give confidence intervals via bootstrap over video IDs, not independent frames. The V2 runner currently reports frame metrics and per-frame JSONL; **video-level uncertainty is pending**.

When the detector already labels a Fake frame as Real before attack, that frame is not a successful adversarial flip. A drop in AUC is not the same event as flipping the 0.5 classification threshold.

## 6. Mechanism measurements (RQ2)

The forward hook captures a **frozen WGSA**:
- `mean`: four signed Haar subband means (original WGSA MLP descriptor).
- `abs_mean`: four absolute-value means (auxiliary statistic).
- `energy`: four mean-squared band responses.
- `gates`: four adaptive outputs from the original MLP.
- `attention`: 2-D normalized attention reconstructed by IDWT.

For every sample compare *the clean and attacked same frame*. Save mean absolute differences (MAE) for each quantity. Attacker gradients can change MobileViT features and its downstream WGSA. **Observed gate drift does not by itself show that the WGSA causes misclassification.** Next-stage controls must include a properly trained backbone-only model, gate-frozen/constant-gate checks, and matching adversarial budgets. Stratify WGSA drift by attack success/failure rather than only global mean; a future mechanism experiment should record the changes for both subsets.

## 7. Exact run sequence (Linux laboratory)

Clone repo at the committed revision and restore the authorized data & SHA-verified public weights. Keep the WGN-compatible PyTorch/TIMM environment; do not blindly install different versions into the reproduction environment.

```bash
cd /lab/special_project
git pull origin main
python -m pytest experiments/EXP-004-ADVERSARIAL-WGN/tests -q

export WGN_REPO_ROOT="$PWD"
export WGN_DATA_ROOT="/lab/data"
export WGN_MANIFEST="/lab/data/FaceForensics++-official.json"
export WGN_CHECKPOINT="/lab/ckpt/experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/best.pt"

bash experiments/EXP-004-ADVERSARIAL-WGN/run_lab_linux.sh
```

Pilot `--max-samples 40 --steps 3` is **only** a smoke test. After verifying output, use a new output path for the locked full test:

```bash
python experiments/EXP-004-ADVERSARIAL-WGN/code/run_exp04_v2.py \
  --repo-root "$WGN_REPO_ROOT" --data-root "$WGN_DATA_ROOT" \
  --manifest "$WGN_MANIFEST" --checkpoint "$WGN_CHECKPOINT" \
  --output "$PWD/exp04_runs/full_c23_seed1024" \
  --compression c23 --methods fgsm pgd jia-faa-adapt \
  --epsilon 0.01568627450980392 --alpha 0.00392156862745098 \
  --steps 10 --batch-size 4
```

For cross-compression use `--compression c40`, same checkpoint SHA and a **different** output directory. When comparing the separate C40-trained model, use the corresponding SHA and document it as a different experiment, not the same-model shift.

Files:
- `environment.json`: checkpoint SHA, manifest SHA, source, attack and seed.
- `<attack>_per_frame.jsonl`: clean/attacked score, video ID, manipulation group, numerical perturbation bound, WGSA drift; only a hash of the absolute frame path.
- `<attack>_summary.json`, `results.json`: defined metrics. Failed runs must not be reported as completed.
- Logs: save stdout/stderr separately outside Git; register experiment artifacts through the repository backup policy after actual runs.

The scripts do not upload private data or weights. Selected results/code/metadata may be committed after research review. **Do not commit raw faces, source videos or secrets.**

## 8. Interpretation, controls and reproducibility gates

1. **Code gate**: CPU tests for DCT reconstruction, input bounds, model-invariance and attack purpose. Verify logits are recomputed after the attack; freeze weights; no leakage of adversarial labels.
2. **Machine gate**: preflight confirms GPU/CUDA, compatible TIMM/PyTorch, manifest and checkpoint SHA, and a pilot 40-frame forward/backward.
3. **Data gate**: before publishing results, independently match the clean AUC/ACC with EXP-002 under identical checkpoint and test records. A mismatch requires debugging, not reinterpretation.
4. **Threat gate**: verify perturbation budgets, attack steps and optional multiple restarts; no unbounded perturbation reported as imperceptible.
5. **Claim gate**: only `jia-faa-adapt` may be used as a **Jia-inspired** attack. It is not Jia's exact Algorithm 1. Hou, Abdullah, Hooda, Shahjahan are *context/defense references* until their actual methods are implemented.
6. **Statistics gate**: stratify ASR and gate drift by manipulation/video, add confidence intervals (video-level bootstrap), and compare successful vs unsuccessful attacks.
7. **Defense gate**: after RQ1/RQ2, compare EXP-005 RCWG against standard adversarial training on unchanged WGN; perform adaptive white-box attacks against the final *defended* model, not only attacks generated on the old WGN.

## 9. Explicit limitations of this V2 implementation

- Without the authors' released implementation/details of adaptive M, **exact Jia-Algorithm-1 reproduction is not verified**. Jia's own `ε=0.1` setting is not directly comparable to an experimental 4/255 pixel budget.
- The current `jia-faa-adapt` is a *custom paper-grounded adaptation*, not a novel attack or a faithful official reproduction.
- No verified Hou StatAttack, MStatAttack, Jia Hybrid Algorithm 2 or D4 evaluation is implemented in V2.
- Mean WGSA drift is a diagnostic, not a causal inference. Video-level robust AUC and bootstrap CI remain work items.
- All metrics from EXP-004 V2 are **pending actual GPU execution**. Never invent results.
