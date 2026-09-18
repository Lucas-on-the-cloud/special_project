# Project Scope

## Working title

**Robust Vision-Based Parking Occupancy Monitoring Across Different Parking Lots and Weather Conditions**

Alternative title after experiments:

**Cross-Domain Parking-Space Occupancy Classification with Weather- and Lighting-Aware Robustness**

## Application problem

A fixed camera observes a parking area. The system receives predefined parking-space polygons, crops each space, classifies it as occupied or vacant, and produces a visual parking map plus the number of available spaces.

The application is straightforward; the research problem is reliability when the environment changes.

## Main research gap

High within-dataset accuracy does not guarantee deployment reliability. Parking datasets contain sequences of highly similar frames, so random image-level splitting may place nearly identical scenes in both training and test sets. A useful project must evaluate unseen cameras/parking lots and weather/lighting shifts.

## Research questions

- **RQ1:** How large is the generalization gap between an in-domain split and an unseen-parking-lot or unseen-dataset test?
- **RQ2:** Does weather- and lighting-aware augmentation reduce this gap?
- **RQ3:** Which lightweight backbone gives the best accuracy–latency trade-off on the same evaluation protocol?

## Hypotheses

- **H1:** Random frame-level splitting produces materially higher scores than parking-lot-separated evaluation.
- **H2:** Weather/lighting augmentation improves macro F1 on unseen parking lots without a large in-domain accuracy loss.
- **H3:** A lightweight backbone can provide application-ready throughput while retaining most of the robust model's accuracy.

## Contribution layers

### 1. Reproducibility contribution

- Reproduce the ACPDS baseline from its public repository.
- Record code revision, environment, split, and discrepancies.
- Supply a Kaggle notebook that another student can rerun.

### 2. Research contribution

- Build a leakage-resistant cross-lot/cross-dataset benchmark.
- Quantify domain shifts by lot, camera, weather, and lighting.
- Compare a simple weather-aware baseline with selected robustness/domain-generalization methods.
- Perform ablation studies so any improvement has an identifiable cause.

### 3. Application contribution

- Convert model predictions into an occupancy overlay and available-space count.
- Benchmark latency, throughput, model size, and memory.
- Demonstrate the system on held-out images or video.

## Main datasets

1. **ACPDS:** first reproduction and pipeline verification.
2. **PKLot:** primary dataset because it includes multiple parking lots and weather categories.
3. **CNRPark+EXT:** external dataset for cross-dataset evaluation.

Tongji ps2.0, SNU, and SUPS are literature/future-work datasets for automatic parking-slot detection. They are not required for the core project.

## Minimum viable capstone

The project is complete at minimum when it contains:

- one reproducible official baseline;
- one modern lightweight baseline;
- a leakage-resistant in-domain and cross-domain evaluation;
- one justified robustness improvement;
- an ablation and error analysis;
- a working occupancy visualization;
- a report that discusses accuracy–efficiency trade-offs and limitations.

## Stretch goals

- MixStyle feature-statistics domain generalization;
- unsupervised Deep CORAL adaptation when unlabeled target images are available;
- Tent test-time adaptation;
- automatic slot localization using a separate detector.

Only one stretch method should be attempted at a time.

## Explicit non-goals

- New end-to-end parking infrastructure or hardware
- License-plate recognition
- Payment/reservation systems
- Multi-object tracking
- Training a large foundation model
- Solving occupancy classification and automatic slot localization simultaneously in the first semester

## Metrics

### Predictive performance

- Accuracy and balanced accuracy
- Macro F1
- Occupied/vacant precision and recall
- Confusion matrix
- AUROC when probability calibration is meaningful

### Deployment performance

- Median and p95 latency
- Crops/spaces processed per second
- Model parameters and file size
- Peak GPU memory

### Robustness breakdowns

- Parking lot/camera
- Sunny, cloudy, rainy, shadow, haze, and night when labels exist
- In-domain versus unseen-lot versus unseen-dataset

## Experimental controls

- Use official sequence/parking-lot splits where available.
- Never randomly mix adjacent frames across train and test.
- Hold seeds, input resolution, training budget, and evaluation code constant in model comparisons.
- Tune on validation data only; do not tune on CNRPark+EXT when it is the external test set.
- Report mean and standard deviation over multiple seeds for the final experiments when compute permits.

## Decision gates

| Gate | Evidence required | Decision |
|---|---|---|
| G1 | ACPDS notebook runs end to end | Move to modern baseline |
| G2 | Cross-lot score is lower than in-domain score | Continue with robustness question |
| G3 | Error breakdown shows weather/lighting sensitivity | Implement targeted augmentation |
| G4 | Augmentation baseline is stable | Try AugMix or MixStyle |
| G5 | Clear accuracy–latency candidate exists | Build application demo |

## Risk and fallback plan

| Risk | Fallback |
|---|---|
| Dataset download or format problems | Finish ACPDS reproduction and create deterministic loaders for PKLot |
| Improvement does not outperform baseline | Report the negative result and analyze conditions/ablation |
| Cross-dataset label mismatch | Map to the common occupied/vacant task and document exclusions |
| Kaggle GPU time limits | Use frozen backbones, smaller input sizes, early smoke runs, and cached crops |
| Automatic slot detection is too complex | Keep predefined polygons; automatic localization remains future work |

## Scope freeze rule

Do not add detection, tracking, license plates, or IoT features before EXP-005 is complete. New ideas belong in a future-work list until the main research question has evidence.

