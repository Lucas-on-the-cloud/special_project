# EXP-003 variant: source-degradation consistency

## Hypothesis

WGN's cross-dataset gap is partly caused by sensitivity to face-crop and media
processing pipelines. Training on two source-only views should improve
invariance without target fine-tuning or extra inference cost.

## Frozen protocol

- Train only on FF++ c23 with the same split, backbone, optimizer, schedule,
  seed, and 25-epoch budget as the new-machine baseline.
- Apply the same degradation distribution to real and fake samples.
- View A uses the existing resize and horizontal flip.
- View B adds crop jitter up to 4%, downscale/upscale (minimum 0.5), JPEG
  quality 30--95, Gaussian blur up to sigma 1.5, and color jitter up to 0.2.
- Both views receive BCE supervision.
- D0 (`degradation_control`) uses lambda 0.
- D1 (`degradation_consistency`) adds
  `0.1 * MSE(sigmoid(logit_A), sigmoid(logit_B))`.
- Validation and inference use the original clean single-view pipeline.
- External targets remain locked; Celeb-DF uses official-direct only.

The comparison D1 versus D0 isolates the consistency term. D0 versus the
baseline measures the effect of degradation augmentation plus the second BCE.
No external test result may change these settings.
