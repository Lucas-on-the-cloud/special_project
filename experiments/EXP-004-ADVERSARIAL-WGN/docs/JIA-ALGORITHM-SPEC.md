# Jia FAA — specification and provenance checkpoint

Date: 2026-11-15. Status: source mapping complete; original-author fidelity remains unresolved for the items below. V3 now implements a completely specified reconstruction under [V3-PROTOCOL.md](V3-PROTOCOL.md); final reconstruction evaluation is permitted with that limited claim.

## Source identity

[Jia et al., CVPR 2022, official CVF PDF](https://openaccess.thecvf.com/content/CVPR2022/papers/Jia_Exploring_Frequency_Adversarial_Attacks_for_Face_Forgery_Detection_CVPR_2022_paper.pdf), checked against the link embedded in the student proposal. Downloaded PDF SHA-256: `974d039100f741ccb1f214b1cd24dff4621fbda72b63f16d950a589c8ca4c363`.

The CVF landing page lists the PDF and arXiv, without a supplementary/code link at the time checked. An authoritative implementation has not been established by this audit. This does not prove that none exists. Search-result references to Tencent/TFace were not sufficient to identify the Jia FAA implementation; references for other papers must not be mistaken for this method's source.

## Historical V2 audit: paper → implementation → verification

| Paper anchor | Current V2 implementation | Verification or required action |
|---|---|---|
| §3 objective / true-label BCE ascent | `loss_fake_to_real`, Fake=1 | Toy gradient direction passes; keep WGN-specific logit/label convention explicit |
| Eq. (5), block orthonormal DCT / IDCT | `attacks.block_transform` | Independently matches SciPy DCT-II; test reconstruction and gradients |
| Eq. (6), weighted additive fusion | `jia_faa_adaptation` | Structural correspondence; M definition not author-verified |
| Eq. (7), accumulated sign-gradient update of P | `jia_faa_adaptation` | Add a deterministic recurrence/gradient test once units and constraint handling are specified |
| Eq. (4), DCT-domain norm constraint | V2 enforces only pixel L∞ | Requires a defined p, coefficient scale, epsilon, and final-output feasibility check |
| Algorithm 1, perturbation initialization | V2 uses `rand_like(x)*alpha` | Different from the stated U(0,1); docstring disagrees with code |
| §3.2 stopping description | V2 returns last iterate | Specify per-sample stopping/selection; retain achieved evasion for evaluation |
| §3.1 PGD baseline | Clean initialization; no restart CLI | Add explicit random-start/restart configuration and strong-baseline checks |
| Algorithm 2 | Not implemented in V2 | Separate later implementation and review; legacy hybrid probe is not a substitute |

## Details that must not be silently invented

**M construction.** The inspected text describes frequency-dependent proportional weights and resetting for different inputs, but does not provide an executable formula covering aggregation, scaling, channels and zero-energy cases. V2's mean-absolute/max-normalized matrix with a 0.1 floor is a project heuristic. Do not assert that resetting for different inputs necessarily means recomputing M each iteration.

**Frequency feasibility.** Specify the norm, whether applied globally/per block/per channel, input numerical range, DCT normalization, and epsilon units. Verify the constraint on the final RGB output after range handling. A pixel-L∞ bound does not establish a same-valued DCT bound. If feasibility requires a new projection procedure, document that procedure as a reconstruction choice unless supported by author code.

**Parameters.** Block size 8, lambda=1/255, N=10 and a pixel epsilon of 4/255 come from the current project configuration. They have not been verified as original FAA values. The paper's explicitly stated 0.1 pixel setting applies to the FGSM/PGD comparison; it must not be assigned to FAA automatically.

**Pseudocode interpretation.** Reconcile the notation for the fusion argument and image update, gradient evaluation point, valid RGB handling, the inclusive loop index and prose stopping rule. Preserve per-sample clean labels and eligibility. Document each operational choice before measuring final-test performance.

## Execution boundary

V3 resolves executable ambiguity through declared choices, not new claims about the authors: P~U(0,1), explicit M policy, accumulated sign-gradient updates, final RGB and DCT-norm feasibility, best BCE and per-image stopping. Independent SciPy/gradient/manual recurrence tests cover these operations. Stable true-Fake BCE avoids FP32 gradient cancellation. PGD adds best iterates and restarts; a paired frequency-initialization control isolates gradient optimization from random corruption. Exact parameters and operational definitions are in V3-PROTOCOL.md, with the initial final configurations in `../code/configs/`.

Environment installation, artifact restoration and CPU software verification can proceed while these source questions are resolved. Full FAA claims require either author-verified details or a completely specified reconstruction clearly labeled as such. Do not replace the unresolved M with an undocumented new heuristic, or call current `jia-faa-adapt` an exact reproduction.

This work evaluates WGN. The EXP-005 draft is outside the present specification.
