# Hou2023 — paper/source audit for a WGN adaptation

Reviewed: 2026-11-15. This document records reading and implementation requirements, not executed attack results. Proposal item2 is Hou et al., **Evading DeepFake Detectors via Adversarial Statistical Consistency**, CVPR2023, pp.12271–12280.

## Primary sources

- [Accepted CVF PDF](https://openaccess.thecvf.com/content/CVPR2023/papers/Hou_Evading_DeepFake_Detectors_via_Adversarial_Statistical_Consistency_CVPR_2023_paper.pdf), SHA256 `7f706ee7c50ced98ad91e0a3479ac79ef65077e1e2d5bee44009b139cc21d548`; cached outside Git at runtime `sources/hou-cvpr2023.pdf`.
- [Authors' arXiv text with supplement](https://arxiv.org/html/2304.11670), especially sections4–6 and8.4. The CVF HTML/supplement URL returned403; the accepted PDF was downloaded and the arXiv supplement was readable.
- [Research source repository at reviewed commit](https://github.com/tobuta/evadingfakedetector/tree/bd62d1f44cf822f665a192aa348925ec6c1fa033), including `attack/stat_attack.py`, `attack/mmd.py`, `attack/blur.py`, `demo.py`, `model/resnet.py` and `utils/dataloader.py`.

## Mechanism to retain

StatAttack composes exposure, adaptive blur and additive noise, then minimizes a real/fake feature MMD objective with regularization. The reference features are taken near the detector's global pooling output. MStatAttack uses multiple layers, with exposure/blur/noise/identity branches mixed by learned softmax weights at each layer; parameters and weights are optimized jointly. The main paper describes40 updates, three layers for MStatAttack and batch30; supplement specifies polynomial degree11, exposure/flow rates0.01/0.001 and blur kernel3.

This changes input RGB and its spatial/frequency statistics. It is not a coefficient-space DCT attack or direct manipulation of WGN's Haar features. Unlike Jia's per-image objective, MMD couples the samples in each batch. Our four WGN datasets replace the original paper's FF++, StyleGANv2, StarGAN and ProGAN setting; original table values are not expected replication targets.

## Source observations and implications

| Reviewed source | Observation | Required handling in EXP-005 |
|---|---|---|
| [`stat_attack.py`](https://github.com/tobuta/evadingfakedetector/blob/bd62d1f44cf822f665a192aa348925ec6c1fa033/attack/stat_attack.py) | Only `StatAttack` is implemented; no MStatAttack file/class in the reviewed tree | Implement/test the multi-layer construction separately; use a reconstruction label |
| Same file | Loss uses MMD and optional penalties; classifier-label CE is absent | Do not add evasion BCE and describe the result as the same objective |
| Same file | Defaults: step10, MMD weight10, bias/flow penalties10/10, noise penalty0; bias/flow/noise/blur rates0.1/0.001/1⁄255/0.1 | Defaults differ from paper/supplement; make a named profile with provenance, not hidden inherited defaults |
| Same file | Positive regularization of rendered bias field and flow differences | Eq.2 prints negative regularization and Eq.7 adds it; coefficient vs rendered-field penalties also differ. Resolve direction and normalization explicitly; do not optimize an unbounded negative penalty blindly |
| Same file | Noise clipped to4⁄255; composed RGB clipped around the original input by60⁄255, then[0,1] by default | These are distinct constraints. Noise bound alone does not bound total exposure/blur change; do not call the total attack4⁄255 |
| Same file | Initializes coefficient/flow/noise at zero, blur map normalized to norm100; returns final image after `step` updates | Record initialization and final-iterate semantics. Do not assume initial blur is identity or add Jia stopping/selection rules |
| [`blur.py`](https://github.com/tobuta/evadingfakedetector/blob/bd62d1f44cf822f665a192aa348925ec6c1fa033/attack/blur.py) | Spatially varying normalized Gaussian weights depend on a squared parameter multiplying distance; tensors are allocated with bare `.cuda()` | Treat parameterization as precision-like rather than silently interpreting it as standard deviation. Make device handling explicit and independently check kernels/gradients |
| [`mmd.py`](https://github.com/tobuta/evadingfakedetector/blob/bd62d1f44cf822f665a192aa348925ec6c1fa033/attack/mmd.py) | Sum of five Gaussian kernels with bandwidth multiplier2; empirical bandwidth is detached; reduction assumes equal fake/reference batch sizes | Preserve estimator/reduction and reference assignment; test degenerate bandwidth and partial batches |
| [`demo.py`](https://github.com/tobuta/evadingfakedetector/blob/bd62d1f44cf822f665a192aa348925ec6c1fa033/demo.py) | Iterates `zip(fake_loader, guidedloader)` and uses local result indices | A finite Real bank would truncate our full Fake corpus; stream/cycle references and use unique record IDs rather than copying this demo loop |
| [`dataloader.py`](https://github.com/tobuta/evadingfakedetector/blob/bd62d1f44cf822f665a192aa348925ec6c1fa033/utils/dataloader.py) | Applies GaussianBlur5×5, sigma0.6 before ToTensor | Do not silently change frozen WGN's clean pipeline. If studied, make a separate declared preprocessing variant and clean baseline |
| [`resnet.py`](https://github.com/tobuta/evadingfakedetector/blob/bd62d1f44cf822f665a192aa348925ec6c1fa033/model/resnet.py) | Expects an unpublished detector weight path and exposes global-pool features by hooks | Replace only the detector adapter with our checksum-verified WGN; no author ResNet weights are needed for WGN white-box evaluation |

The repository's [MStatAttack request](https://github.com/tobuta/evadingfakedetector/issues/1) and [weight-path issue](https://github.com/tobuta/evadingfakedetector/issues/3) are consistent with the inspected omissions. Their existence does not supply missing code/details. Do not claim there is no implementation anywhere; the statement is scoped to the pinned tree reviewed here.

## WGN-specific decisions proposed for implementation

Use the classifier's input vector (fusion output after spatial mean pooling), dynamically sized from the model; keep the whole MobileViT/WGSA/fusion path differentiable. Reference features may be cached with no gradients, while attacked features must remain attached. Preserve weights, buffers, preprocessing and threshold.

The primary reference bank is separate FF++ train Real, shared across all evaluation datasets. This makes the real-reference access assumption explicit and avoids using evaluation Real to guide the main attack. Real/fake subjects need not be paired for this distribution loss. Source/identity separation beyond known split metadata must not be assumed.

Zero RGB values, tiny Gaussian parameters, all-identical features, final partial batches, stale hooks and changing batch composition require numerical/coverage tests. The existing EXP-004 `statistical_proxy` omits core MMD/optimization and is not an implementation baseline for this study.

## Fidelity decision

The [executable specification](HOU-ALGORITHM-SPEC.md) resolves the choices for the named source-adapted40 profile. The implementation passed CPU tests and actual-WGN CUDA clean/smoke gates; both methods and matched initialization controls completed all four full cohorts, and per-dataset audits passed. Method names are `hou-statattack-wgn-adapted` and `hou-mstatattack-reconstruction`; neither promises exact recovery of the original experiment. The paper/source differences above remain provenance, not unresolved hidden defaults in the executed profile. Full-cohort outcomes are summarized in the [EXP-005 README](../README.md#full-cohort-results) with per-dataset reports alongside it.
