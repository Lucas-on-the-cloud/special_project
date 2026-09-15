# Code-First Reproducibility Priority

## Why this matters

This capstone is expected to be developed largely independently, so paper selection should prioritize **reproducibility**, not only novelty or citation count.

The default selection order for implementation-related papers is:

```text
Official code + public data + runnable instructions
                    ↓
Official code + accessible data
                    ↓
Public data + standard framework implementation
                    ↓
Paper with method description but no code
```

A strong paper without code may still be important for the literature review, but it should not automatically become the main implementation target.

---

## Reproducibility Tiers

### Tier A — Preferred for reproduction

These resources have public code and data and are the safest starting points for independent work.

#### ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification

Paper:
https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html

Official repository:
https://github.com/usuyama/ePillID-benchmark

Why it is high priority:

- public benchmark data
- training/evaluation source code
- environment instructions
- Docker setup
- tutorial Colab notebook
- clear baseline methodology

Recommended use:

- learn the complete research-to-code workflow
- reproduce a published pill-recognition baseline
- study fine-grained and visually similar pill classes

---

#### Multi-stream Fusion for Class Incremental Learning in Pill Image Classification (CG-IMIF)

Paper:
https://openaccess.thecvf.com/content/ACCV2022/html/Nguyen_Multi-stream_Fusion_for_Class_Incremental_Learning_in_Pill_Image_Classification_ACCV_2022_paper.html

Official repository:
https://github.com/vinuni-vishc/CG-IMIF

Why it is high priority:

- official implementation
- requirements/environment files
- VAIPE-PCIL dataset preparation
- reproducible experimental setup
- directly related to the VAIPE research ecosystem

Recommended use:

- study how VAIPE-derived data are processed
- learn experiment organization
- possible auxiliary experiment if continual learning becomes relevant

---

## Tier B — Useful data / partial reproducibility

### Few-Shot Pill Recognition (CURE)

Paper:
https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html

Author repository:
https://github.com/suiyiling/Few-shot-pill-recognition

Current reproducibility assessment:

- public CURE dataset link is provided
- author repository is available
- repository is useful as the authoritative dataset source
- implementation support appears more limited than ePillID

Recommended use:

- dataset / benchmark comparison
- robustness experiments involving background, illumination, and zoom
- do not make reproduction of the original full method a first milestone

---

### VAIPE / PGPNet

Paper:
https://doi.org/10.1371/journal.pone.0291865

Dataset:
https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset

Current reproducibility assessment:

- highly relevant public multi-pill dataset
- prescription-related contextual information
- excellent problem-defining paper for this capstone
- no official PGPNet implementation has been confirmed in the current review

Recommended strategy:

**Use VAIPE as the primary dataset, but initially train a standard detector with well-maintained public code instead of reimplementing PGPNet from scratch.**

Possible baseline:

```text
VAIPE
  ↓
YOLO / RT-DETR baseline
  ↓
Medication detections
  ↓
Prescription matching
  ↓
Verification experiments
```

A community VAIPE challenge solution is available here:
https://github.com/lynguyenminh/VAIPE2022.Medicine-Pill-Image-Recognition

However, this is not treated as the official implementation of the PGPNet paper and should be used only as an additional engineering reference.

---

## Tier C — Literature / system-design references

The following papers can still be important even when their exact implementation or private experimental data are unavailable:

- smart medication dispensing platforms
- visual + weight verification systems
- clinical medication-recognition studies
- medication safety studies

Their role is mainly to support:

- motivation
- system architecture
- research-gap analysis
- evaluation design
- discussion of practical limitations

They should not be selected as the main reproduction target unless source code and usable data are later confirmed.

---

## Baseline Model Policy

For the core implementation, prefer models with mature and documented repositories.

### Preferred first baseline

**Ultralytics YOLO**

Reasons:

- straightforward dataset conversion
- strong documentation
- simple training and evaluation API
- easy to run on Kaggle
- object-detection metrics included
- suitable for establishing a baseline quickly

### Possible comparison model

**RT-DETR**

Use only after the YOLO baseline is working reliably.

The project should avoid implementing a complex detector from the paper alone before a reproducible baseline exists.

---

## Paper Selection Checklist

Before adding an implementation paper to the high-priority reading list, check:

- [ ] Is there an official or author-maintained repository?
- [ ] Is the dataset public or realistically obtainable?
- [ ] Are training instructions available?
- [ ] Are dependency versions documented?
- [ ] Are pretrained weights available?
- [ ] Is evaluation code available?
- [ ] Can the method run on Kaggle / Colab / available GPU resources?
- [ ] Are open issues understandable and manageable?
- [ ] Is the license compatible with academic research?

The more boxes that are checked, the higher the implementation priority.

---

## Practical Reading Priority

For independent development, the current recommended order is:

1. **VAIPE / PGPNet paper** — understand the main problem and dataset.
2. **ePillID paper + official repository** — reproduce a complete published pill-recognition pipeline.
3. **VAIPE dataset + YOLO baseline** — begin the actual capstone baseline.
4. **CG-IMIF paper + repository** — study a second reproducible VAIPE-related research implementation.
5. **CURE paper + dataset** — investigate robustness and fine-grained recognition.
6. Smart-dispenser papers — use mainly for architecture, motivation, and system comparison.

---

## Rule for This Project

> **Do not spend several weeks reimplementing a paper with no code unless the method becomes essential to the final research contribution.**

The first priority is to build a working, measurable, reproducible baseline. Novel method development should start only after the dataset, evaluation pipeline, and baseline are stable.
