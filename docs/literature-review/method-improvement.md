# Method Improvement Plan

The first improvement should target an observed failure, not add complexity for its own sake. Establish a modern baseline and a cross-lot/cross-dataset gap before using these methods.

## Five method papers

| Method | Core idea | Why it may help parking occupancy | Complexity | Paper/code |
|---|---|---|---:|---|
| RandAugment | Search-free augmentation controlled mainly by operation count and magnitude | Low-cost baseline for varied color, contrast, geometry, and illumination | Low | [Paper](https://arxiv.org/abs/1909.13719); implementation available in `torchvision.transforms` |
| AugMix | Mixes several stochastic augmentation chains and adds a consistency objective | Designed to improve robustness to common visual corruptions without destroying clean accuracy | Low–medium | [Paper](https://arxiv.org/abs/1912.02781), [official code](https://github.com/google-research/augmix) |
| MixStyle | Mixes feature statistics between training instances to synthesize domain styles | Parking-lot shift often appears as camera/background/weather “style” changes | Medium | [Paper](https://arxiv.org/abs/2104.02008), [official code](https://github.com/KaiyangZhou/mixstyle-release) |
| Deep CORAL | Aligns second-order feature statistics between source and unlabeled target domains | Useful when unlabeled images from the deployment lot are available | Medium | [Paper](https://arxiv.org/abs/1607.01719) |
| Tent | Adapts normalization parameters at test time by minimizing prediction entropy | Tests whether online unlabeled adaptation helps changing weather/cameras | Medium–high | [Paper](https://arxiv.org/abs/2006.10726), [official code](https://github.com/DequanWang/tent) |

For evaluation design, also consult the [common-corruptions robustness benchmark](https://github.com/hendrycks/robustness). It is a benchmark reference, not one of the five selected improvement methods.

## Stage 0 — Domain-specific augmentation baseline

Before the five published methods, create a transparent manual baseline using Albumentations:

- brightness/contrast and gamma;
- color temperature or hue/saturation shift;
- shadow and sun flare, used conservatively;
- rain, fog/haze, blur, and sensor noise;
- small perspective/affine perturbations;
- random erasing/occlusion.

Every transform must be visually inspected on parking-space crops. Excessive weather simulation can change the label evidence and make the experiment meaningless.

## Proposed experiment sequence

| Stage | Train method | Target labels used? | Main comparison |
|---:|---|---:|---|
| M0 | Standard resize/crop/flip | No | Clean baseline |
| M1 | Manual weather/lighting augmentation | No | Does targeted augmentation address observed errors? |
| M2 | RandAugment | No | Simple generic augmentation versus manual policy |
| M3 | AugMix | No | Corruption robustness and consistency training |
| M4 | MixStyle | No | Domain generalization without target access |
| M5 | Deep CORAL | No labels; unlabeled target images | Unsupervised domain adaptation |
| M6 | Tent | No labels; online target batches | Test-time adaptation |

Only M0–M4 belong to the primary “unseen domain” comparison. Deep CORAL and Tent use target-domain images and must be reported in a separate adaptation setting.

## Ablation design

For each selected method, hold constant:

- backbone and initialization;
- input resolution;
- optimizer, schedule, epochs, and batch size;
- dataset split and seeds;
- model-selection metric;
- evaluation code.

Report:

- in-domain and unseen-lot macro F1;
- PKLot → CNRPark+EXT macro F1;
- per-condition errors;
- training cost and inference latency;
- mean ± standard deviation for final comparisons when compute permits.

## Decision rules

1. If the cross-domain drop is small, prioritize the lightweight application rather than adding adaptation methods.
2. If weather/lighting errors dominate, compare manual augmentation, RandAugment, and AugMix first.
3. If the shift is strongly camera/style dependent, try MixStyle.
4. Use Deep CORAL only when unlabeled target-lot images are a realistic deployment assumption.
5. Use Tent only after the static model is stable and target batches are well-defined.
6. Stop adding methods when the evidence answers the research question; five implemented methods are not required.

## Recommended undergraduate contribution

The recommended final method is intentionally modest:

> A leakage-resistant cross-lot benchmark plus a weather/lighting-aware training policy, evaluated against one generic augmentation method and one feature-level domain-generalization method.

That yields a defensible contribution without turning the capstone into a risky architecture-design project.

