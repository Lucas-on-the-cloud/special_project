# Capstone Project Proposal

## Title

**Robust Vision-Based Parking Occupancy Monitoring Across Different Parking Lots and Weather Conditions**

**Project type:** Undergraduate Special Project / Capstone Project  
**Duration:** Two semesters  
**Compute:** Kaggle notebooks and public datasets

## 1. Background and motivation

Camera-based parking monitoring can estimate which parking spaces are occupied without installing a physical sensor in every space. A practical system can display free spaces, help drivers locate parking, and support parking-lot management.

Parking-space classifiers often achieve high accuracy when training and testing on images captured by the same camera. However, real deployment introduces changes in camera viewpoint, parking-lot layout, background, weather, illumination, shadows, and image quality. Video datasets also contain many near-duplicate frames. If adjacent frames are randomly divided between training and test sets, reported performance may overestimate the ability to generalize.

This project therefore focuses on **robust occupancy classification**, not only high accuracy on one dataset.

## 2. Problem definition

The initial application assumes a fixed camera and known parking-space polygons:

```text
Parking-lot image
        ↓
Predefined parking-space polygons
        ↓
Crop each parking space
        ↓
Occupied / vacant classifier
        ↓
Parking-map overlay + available-space count
```

The central research problem is:

> How can a lightweight visual parking-space classifier remain reliable when the parking lot, camera, weather, or illumination differs from its training data?

### Research questions

1. How much does performance decline on an unseen parking lot or external dataset?
2. Can weather- and lighting-aware augmentation reduce this generalization gap?
3. Which lightweight backbone provides the best accuracy–latency trade-off for a practical monitoring system?

## 3. Proposed contributions

### C1. Leakage-resistant evaluation

Create reproducible splits separated by parking lot, camera, capture session, or official sequence. Compare these results with conventional in-domain evaluation and document the effect of near-duplicate-frame leakage.

### C2. Robustness improvement

Build a transparent weather/lighting augmentation baseline, then compare it with selected published methods such as RandAugment, AugMix, or MixStyle. The project will add a method only when error analysis supports it.

### C3. Application and efficiency study

Build a working image/video prototype that overlays occupancy status and counts free spaces. Compare accuracy, macro F1, latency, throughput, memory, and model size for lightweight backbones.

The intended undergraduate contribution is an evidence-based evaluation and practical improvement—not a new large neural-network architecture.

## 4. Data and reproducibility strategy

### ACPDS — first reproduction

The paper *Image-Based Parking Space Occupancy Classification: Dataset and Baseline* provides a small public dataset, annotations, code, and pretrained resources. It will be used to learn and verify the complete reproduction workflow.

- Paper: https://arxiv.org/abs/2107.12207
- Official repository: https://github.com/martin-marek/parking-space-occupancy

### PKLot — main benchmark

PKLot contains images from multiple parking lots and weather conditions. It supports leave-one-parking-lot-out and weather-aware experiments.

- Dataset: https://web.inf.ufpr.br/vri/databases/parking-lot-database/
- Paper: https://doi.org/10.1016/j.eswa.2015.02.009

### CNRPark+EXT — external evaluation

CNRPark+EXT provides another camera environment and will serve as an external test set for measuring cross-dataset generalization.

- Paper/data record: https://openportal.isti.cnr.it/doc?id=people______::f0ae3d0d7a052b367753c8a217c77897

Dataset archives and model weights will not be committed to Git. The repository will store notebooks, data manifests, split definitions, configurations, compact metrics, and selected figures.

## 5. Methodology

### Stage 1 — Reproduce and verify

1. Run the official ACPDS code on Kaggle.
2. Record the Git revision, packages, hardware, data counts, split, and metrics.
3. Document discrepancies between the paper, repository, and current environment.

### Stage 2 — Establish modern baselines

Train lightweight classifiers such as ResNet18, MobileNetV3, and EfficientNet-B0 under the same input resolution, training budget, and split. Select one baseline before adding improvements.

### Stage 3 — Measure the domain gap

Evaluate:

- in-domain validation;
- leave-one-parking-lot-out testing on PKLot;
- frozen PKLot-to-CNRPark+EXT transfer.

Break errors down by parking lot, camera, weather, lighting, and class.

### Stage 4 — Improve robustness

Compare the standard baseline with:

1. manual weather/lighting augmentation;
2. RandAugment or AugMix;
3. MixStyle if camera/style shift remains dominant.

Deep CORAL or Tent will be optional because they assume access to unlabeled target-domain images.

### Stage 5 — Build the application

Load an image or video, crop known parking spaces, classify each crop, draw colored polygons, and show the number of occupied and free spaces. Benchmark latency and throughput on a consistent environment.

## 6. Evaluation

### Classification metrics

- accuracy and balanced accuracy;
- macro F1;
- occupied/vacant precision and recall;
- confusion matrix;
- AUROC when appropriate.

### Efficiency metrics

- median and p95 inference latency;
- spaces processed per second;
- parameter count and model-file size;
- peak GPU memory.

### Experimental rules

- Never randomly distribute adjacent frames across train and test.
- Tune hyperparameters on validation data only.
- Keep training budget and evaluation code constant in comparisons.
- Separate zero-shot cross-dataset evaluation from adaptation using target images.
- Report multiple seeds for final comparisons when Kaggle compute permits.

## 7. Expected outcome

The expected result is a reproducible parking-occupancy benchmark, an experimentally justified robustness method, and an end-to-end monitoring prototype. Even if a proposed method does not improve accuracy, a controlled negative result with error analysis remains a valid research outcome.

## 8. Scope and risk control

The first version excludes automatic parking-slot localization, license-plate recognition, tracking, payments, reservations, and IoT sensors. Known parking-space polygons keep the project feasible when advisor support and compute are limited.

If cross-dataset training is difficult, the fallback is a complete ACPDS reproduction plus a parking-lot-separated PKLot benchmark, one augmentation study, and the application demo.

## 9. Semester 1 milestones

| Period | Deliverable |
|---|---|
| Weeks 1–2 | Scope, literature map, ACPDS reproduction |
| Weeks 3–5 | PKLot preparation and lightweight baselines |
| Weeks 6–7 | Cross-lot and cross-dataset evaluation |
| Weeks 8–10 | Weather/lighting augmentation experiments |
| Weeks 11–12 | RandAugment/AugMix and optional MixStyle |
| Weeks 13–14 | Ablations and efficiency benchmark |
| Weeks 15–16 | Parking-monitoring prototype |
| Weeks 17–18 | Consolidated results and Semester 1 report |

## 10. Success criteria

The Semester 1 project is successful when it contains:

- one verified official reproduction;
- one modern lightweight baseline;
- one leakage-resistant unseen-lot evaluation;
- one cross-dataset result or documented feasibility limitation;
- one justified robustness experiment with ablation;
- one working occupancy visualization;
- complete experiment records sufficient for another student to rerun the work.

