# Executable Hou/WGN adaptation v1

Status: implemented and CPU-tested; real-WGN CUDA clean/smoke gates execute automatically after EXP-004. This is **source-adapted StatAttack40** and an **explicit MStatAttack reconstruction**, not an exact reproduction of the paper's original detector/dataset experiments. Reviewed upstream commit: `bd62d1f44cf822f665a192aa348925ec6c1fa033`.

## Declared operators and loss

1. Input is the unchanged WGN RGB256×256 crop in[0,1]. WGN parameters and buffers are frozen in eval mode. Features are the fused activation spatial mean immediately before its existing classifier; both WGSA and backbone remain in the gradient path.
2. Exposure uses a degree11 two-dimensional polynomial, with78 coefficients shared across RGB, sampled through a learned spatial flow. The flow grid is32×32, bilinearly upsampled with align_corners=False, then grid_sample uses align_corners=True and coordinates clamped to[-1,1]. Output is `x*exp(clamp(field,-20,20))`. Multiplication is the continuous extension of the source's log/exp expression to zero pixels. The log-field clamp is an explicit numerical safeguard, not an author-verified constraint.
3. Blur uses normalized3×3 spatially varying per-channel weights proportional to `exp(-distance_squared*precision_squared/2)` and reflection padding. This matches the reviewed code's precision-like parameterization, not a silent substitution of Gaussian standard deviation. Per-image precision initializes to constant `100/sqrt(3*H*W)`.
4. Noise initializes to zero and is clipped after each update to[-4/255,4/255]. Coefficients and flow initialize to zero. StatAttack composes exposure→blur→noise. Its initialization-only control includes the same initial blur and need not equal clean.
5. After each layer, clamp composed RGB to the intersection of[0,1] and the clean-origin pixel L∞ ball60/255. This total bound is different from the noise bound. Applying a shared clean-origin bound after each MStat layer is a project feasibility choice; it is not inferred from Eq.8.
6. MMD is the biased equal-batch estimator from the reviewed `mmd.py`: sum of five RBF kernels with bandwidth multipliers1/4,1/2,1,2,4. The central bandwidth is mean off-diagonal squared feature distance of the concatenated fake/reference batch, detached from autograd, floored at1e-12 for degenerate batches. Do not substitute logits or a per-image distribution loss.
7. Minimize `10*MMD + 10*B + 10*S`. B is the sum of squared rendered, unclamped exposure field divided byH*W; S is the sum of squared horizontal/vertical low-resolution flow differences divided by8². These positive field/flow penalties follow the source implementation's behavior. The main paper prints a different coefficient-based regularizer/sign; this profile chooses the source explicitly. No classification CE or extra noise penalty is added.
8. Normalize each parameter gradient by its per-image L1 norm, using1 for a zero norm. Momentum decay1. Update by subtracting the sign of accumulated momentum times the parameter's learning rate. Rates: coefficients0.1, flow0.001, blur precision0.1, noise1/255. Forty updates are followed by a final forward; no41st update, per-image first-evasion stop or best-logit substitution. The40-update count is taken from the paper; the coefficient rate differs from the supplement's0.01 and is retained from source0.1.

## MStatAttack reconstruction

There are3 sequential layers. At each layer, exposure, blur, additive noise and identity all receive the same previous-layer input, and four per-image logits produce softmax mixture weights. Every layer has independent degradation parameters; logits initialize to zero (uniform weights) and use sign-momentum learning rate0.1. All parameters/logits are optimized jointly for40 updates through all layers. Regularization B and S is averaged over the3 layers to keep its scale explicit. These init/rate/reduction/bound choices are declared reconstruction decisions; the reviewed upstream tree does not include MStatAttack code.

Each method has a matched zero-update control with exactly the same initialization/composition. No promise that final MMD, classifier score, or ASR monotonically improves at every step; numerical finiteness and feasibility are enforced. MMD values and all mixture weights are logged at batch boundaries.

## References, grouping and eligibility

Use960 FF++ train-only Real frames selected deterministically with seed1024 and video round-robin. They cover720 training videos; image hashes, source-shard checksums and split disjointness are recorded in `exp05-runtime/reference-bank.json`. Real guidance is an attacker-access assumption, not training or evaluation leakage from the four test sets.

Cache frozen pooled reference vectors with evaluation batch32. Optimize30 eligible Fake at a time against30 cyclic bank references; final partial batch n uses n references. Assignment begins at eligible offset modulo960, identical across methods. Every eligible Fake is covered; bank length cannot truncate the loader.

Eligibility and baseline clean scores come from the canonical full EXP-004 paired records. Fresh pre-attack scoring uses padded batch32; it must preserve the canonical class at threshold0.5 or the run stops. Rechecked probabilities and absolute deviations are retained because CUDA can differ numerically across batch shapes; they do not replace canonical scores or change the ASR denominator. A full DFDC preflight found zero class changes among42,932 eligible Fake rows, with maximum absolute deviation0.001355052. Real and baseline false-negative Fake rows are copied unchanged for ACC/AUC. Source-pair/video/sequence clusters are inherited. These adaptations separate optimization grouping from canonical evaluation and do not redefine ASR denominators.

## State, provenance and gates

SQLite commits metrics and reference/parameter traces atomically per completed batch. A resume verifies source/config/bank/checkpoint/cohort identities and replays only an uncommitted batch; no stateful optimizer/RNG trajectory crosses batch boundaries because initialization is deterministic. Real image outputs are not stored as a full float32 corpus. Selected examples and float32 arrays remain outside Git.

The queue waited for EXP-004 success, reran all four clean gates, checked actual-WGN feature/logit agreement, finite gradients, RGB bounds, parameter/buffer immutability and VRAM on120 validation Fake frames for all four methods, and completed full evaluation of all four cohorts. Each full-run audit passed. BRISQUE is not implemented in this profile; PSNR/SSIM, norms and finite counts are reported. No original Hou-table/black-box/causal-defense claim is made.
