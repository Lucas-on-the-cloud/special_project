# Literature Review Tracker

Tentative topic:

**Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

This file contains the first **15 verified core papers** for the project. Because the project will be developed largely independently, implementation priority is based not only on scientific relevance but also on **availability of code, public data, and reproducible instructions**.

> For implementation work, prefer: **official code + public data + runnable instructions**. Papers without code remain useful for background, architecture, and research-gap analysis.

See also: [`reproducibility-priority.md`](reproducibility-priority.md)

---

## Core Papers and Reproducibility Priority

| # | Paper | Year | Role | Reproducibility | Code / data | Priority |
|---:|---|---:|---|---|---|---|
| 1 | [A Comprehensive Review of Pill Image Recognition](https://doi.org/10.32604/cmc.2025.060793) | 2025 | Field overview | Review only | Reviews NLM, ePillID, CURE, VAIPE, VAIPE-PCIL | High for reading |
| 2 | [High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion](https://doi.org/10.1371/journal.pone.0291865) | 2023 | Primary VAIPE / prescription-context paper | **Public data; official PGPNet code not confirmed** | [VAIPE dataset](https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset) | **Very high for problem/data; medium for reproduction** |
| 3 | [ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification](https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html) | 2020 | Fine-grained benchmark | **Excellent** | [Official repo: code + data + tutorial](https://github.com/usuyama/ePillID-benchmark) | **Very high for reproduction** |
| 4 | [Few-Shot Pill Recognition](https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html) | 2020 | CURE benchmark / robustness | Good for dataset; implementation support is more limited | [Author repo + CURE data](https://github.com/suiyiling/Few-shot-pill-recognition) | High for data, medium for reproduction |
| 5 | [The National Library of Medicine Pill Image Recognition Challenge: An Initial Report](https://doi.org/10.1109/AIPR.2016.8010584) | 2016/2017 | Benchmark history | Public government data | [C3PI / RxIMAGE data](https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi) | Medium |
| 6 | [Development of fine-grained pill identification algorithm using deep convolutional network](https://doi.org/10.1016/j.jbi.2017.09.005) | 2017 | Historical fine-grained method | Code not prioritized | Paper datasets / method description | Background |
| 7 | [An Accurate Deep Learning-Based System for Automatic Pill Identification: Model Development and Validation](https://doi.org/10.2196/41043) | 2023 | Visual + imprint identification | Partial reproducibility | Uses open medication databases | Background / method ideas |
| 8 | [Effects of Background Colors, Flashes, and Exposure Values on the Accuracy of a Smartphone-Based Pill Recognition System Using a Deep Convolutional Neural Network](https://doi.org/10.2196/26000) | 2021 | Robustness study | Method reproducible conceptually; exact setup custom | Experimental study | High for experiment design |
| 9 | [Multi-stream Fusion for Class Incremental Learning in Pill Image Classification](https://openaccess.thecvf.com/content/ACCV2022/html/Nguyen_Multi-stream_Fusion_for_Class_Incremental_Learning_in_Pill_Image_Classification_ACCV_2022_paper.html) | 2022 | VAIPE-derived continual learning | **Excellent** | [Official CG-IMIF code + VAIPE-PCIL](https://github.com/vinuni-vishc/CG-IMIF) | **Very high for reproduction** |
| 10 | [Enhanced Multi-Pill Detection and Recognition Using VFI Augmentation and Auto-Labeling for Limited Single-Pill Data](https://doi.org/10.1109/ACCESS.2025.3557569) | 2025 | Recent multi-pill detection | Code not yet confirmed | See paper | Background unless code is found |
| 11 | [Code-Based Versus AutoML Methods for Pill Recognition in Clinical Settings: Comparative Performance Study](https://doi.org/10.2196/79160) | 2026 | Clinical YOLO11 evaluation | Model framework is public; clinical data not fully public | YOLO11 + AutoML | High for model/evaluation ideas |
| 12 | [A hybrid framework for pill identification using convolutional neural networks and optical character recognition](https://doi.org/10.1007/s44163-026-01405-x) | 2026 | CNN + OCR | Uses public datasets; exact code availability not prioritized | C3PI, ePillID and other public sets | Medium |
| 13 | [Design and Validation of a Cyber-Physical Medication Dispensing Platform Integrating Edge AI Verification, Distributed Control, and Cloud Synchronization](https://doi.org/10.3390/s26123823) | 2026 | Closest end-to-end smart dispenser | Custom system/data | No implementation target | **Very high for architecture, low for reproduction** |
| 14 | [Design and Implementation of a Smart Medication Dispensing System with Visual and Weight-Based Verification for Patient Safety](https://doi.org/10.1109/ELECO69582.2025.11329260) | 2025 | Vision + weight verification | Custom prototype | Custom data | Architecture reference |
| 15 | [A Vision-Guided, IoT-Integrated Pill Dispensing System for Intelligent Medication Adherence](https://doi.org/10.1109/EDCT65302.2025.11495984) | 2025 | Vision + IoT dispenser | Custom prototype | Custom data | Architecture reference |

---

## Recommended Reproduction Path

The project should **not** attempt to reproduce all 15 papers.

A practical independent-development path is:

### Reproduction 1 — ePillID

Use the official ePillID repository to understand:

- environment setup,
- dataset loading,
- published training/evaluation workflow,
- fine-grained medication recognition,
- reproducible research organization.

Repository:
https://github.com/usuyama/ePillID-benchmark

### Reproduction 2 — VAIPE-related code

Use VAIPE as the main capstone dataset but start with a **standard, maintained detector** such as Ultralytics YOLO rather than rebuilding PGPNet without official code.

```text
VAIPE dataset
    ↓
YOLO baseline
    ↓
Detection + counting
    ↓
Prescription matching
    ↓
Verification metrics
```

A community VAIPE challenge implementation can be used only as an engineering reference:

https://github.com/lynguyenminh/VAIPE2022.Medicine-Pill-Image-Recognition

It should **not** be described as the official PGPNet implementation.

### Reproduction 3 — CG-IMIF

Use the official CG-IMIF repository as a second example of a reproducible VAIPE-related research pipeline:

https://github.com/vinuni-vishc/CG-IMIF

This is optional unless continual/class-incremental learning becomes relevant to the final research question.

---

## Baseline Technology Policy

For implementation, prefer mature frameworks with strong documentation.

### Primary baseline

**Ultralytics YOLO**

Why:

- simple Kaggle/Colab workflow,
- maintained public implementation,
- standard detection metrics,
- easy dataset conversion,
- pretrained weights,
- straightforward inference and visualization.

### Secondary baseline

**RT-DETR** or another public detector may be added after the YOLO baseline is stable.

Do not spend several weeks implementing a complex detector from a paper before the complete baseline/evaluation pipeline works.

---

## Reading Order

### Stage 1 — Define the problem

1. Review paper (#1)
2. VAIPE / PGPNet (#2)
3. Cyber-physical dispenser (#13)

### Stage 2 — Read papers you can actually reproduce

4. ePillID (#3) + run official code
5. CURE (#4) + inspect dataset
6. CG-IMIF (#9) + inspect/run official code

### Stage 3 — Design experiments

7. Capture robustness paper (#8)
8. Clinical YOLO11 paper (#11)
9. Recent multi-pill detection paper (#10)

### Stage 4 — System/background reading

10. Smart dispenser papers (#14, #15)
11. Other identification/OCR papers as needed

---

## Paper Selection Checklist

Before making a paper an implementation priority:

- [ ] Official/author-maintained repository exists
- [ ] Public dataset is accessible
- [ ] Training instructions exist
- [ ] Dependency/environment instructions exist
- [ ] Pretrained weights exist, if applicable
- [ ] Evaluation code exists
- [ ] Runnable on Kaggle / Colab / available GPU
- [ ] License permits academic use

Papers satisfying most of these conditions should be implemented before papers that require full reimplementation from scratch.

---

## Detailed Review Table

| Paper | Task | Dataset | Code status | Can reproduce? | Main metric | Key result | Failure case | Useful idea / gap |
|---|---|---|---|---|---|---|---|---|
| #1 Review |  |  | N/A | N/A |  |  |  |  |
| #2 VAIPE / PGPNet |  |  | Data public; official method code not confirmed | Partial |  |  |  |  |
| #3 ePillID |  |  | Official | Yes |  |  |  |  |
| #4 CURE |  |  | Author repo/data | Partial |  |  |  |  |
| #5 NLM Challenge |  |  | Public data | Baseline possible |  |  |  |  |
| #6 Fine-grained DCN |  |  | Not priority |  |  |  |  |  |
| #7 Automatic Pill ID |  |  | Partial |  |  |  |  |  |
| #8 Capture Robustness |  |  | Custom experiment | Conceptually |  |  |  |  |
| #9 CG-IMIF |  |  | Official | Yes |  |  |  |  |
| #10 Multi-Pill + VFI |  |  | To verify |  |  |  |  |  |
| #11 Clinical YOLO11 |  |  | Framework public, data limited | Partial |  |  |  |  |
| #12 CNN + OCR |  |  | To verify |  |  |  |  |  |
| #13 Edge-AI Dispenser |  |  | Custom | No need |  |  |  |  |
| #14 Vision + Weight |  |  | Custom | No need |  |  |  |  |
| #15 Vision + IoT |  |  | Custom | No need |  |  |  |  |

---

## Project Rule

> **A working, measurable baseline is more valuable than spending weeks recreating an undocumented research implementation.**

The intended contribution should not be merely “use YOLO to recognize pills.” The stronger direction remains **prescription-aware multi-pill verification and dispensing-error detection**, built on reproducible components.
