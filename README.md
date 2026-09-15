# AI-Assisted Medication Verification for Smart Prescription Dispensing

## Overview

This repository documents the development of my undergraduate **Special Project / Capstone Project**.

The project is a **6-credit research project conducted over one academic year**:

- Semester 1: 3 credits, 18 weeks
- Semester 2: 3 credits, 18 weeks
- Total duration: 36 weeks

The current research direction focuses on **computer-vision-based medication verification for smart dispensing systems**. The central idea is to compare the medications detected in an image with the medications expected from an electronic prescription and determine whether the dispensing event is correct.

> **Project status:** research direction recently pivoted from UAV small-object detection to medication verification. The topic is still tentative and will be refined through literature review and baseline experiments.

---

## Tentative Research Topic

**Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

Alternative working title:

**AI-Assisted Medication Verification for Smart Prescription Dispensing**

The project does **not** aim to let AI prescribe medication or make clinical decisions. AI is used as an independent visual verification layer after a prescription has already been created.

---

## Research Motivation

A smart medication dispenser can retrieve a prescription and mechanically dispense medicine, but a complete system also needs a way to verify that the physical output matches the prescription.

A possible workflow is:

```text
Patient / Prescription ID
          ↓
Electronic Prescription
          ↓
Expected Medication List
          ↓
Smart Dispensing Process
          ↓
Camera Image of Dispensed Pills
          ↓
Computer Vision Model
          ↓
Detected Medication + Quantity
          ↓
Expected vs Detected Comparison
          ↓
     MATCH / MISMATCH
```

The research focus is therefore not simply *"Can a model recognize pills?"* but rather:

> **How reliably can a vision-based verification system detect medication dispensing errors by comparing multi-pill detections with an electronic prescription?**

This creates a research problem that combines:

- Multi-pill object detection
- Fine-grained visual recognition
- Medication counting
- Prescription-aware verification
- Dispensing-error detection
- Safety-oriented evaluation

---

## Research Questions

### RQ1
How accurately can modern object-detection models identify and count multiple medications in a single image?

### RQ2
How reliably can the system detect simulated dispensing errors such as missing, extra, and incorrect medication?

### RQ3
How do confidence thresholds, occlusion, pill density, lighting, and visually similar medications affect verification performance?

### RQ4
Can prescription information be used as contextual information to reduce medication-verification errors compared with vision-only prediction?

RQ4 is exploratory and may be refined after the baseline experiments.

---

## Project Scope

### In scope

- Public medication-image datasets
- Multi-pill detection and classification
- Medication counting
- Electronic-prescription representation
- Prescription-to-image matching
- Simulated dispensing-error generation
- Comparison of computer vision models
- Error analysis and robustness experiments
- Prototype verification API or dashboard if time permits

### Out of scope

- AI-generated prescriptions
- Diagnosis or treatment recommendation
- Clinical deployment
- Testing on real patients
- Hospital information-system integration
- Claims that the prototype is a certified medical device

Because access to real clinical dispensing data is limited, the research will primarily use **public datasets and reproducible simulated dispensing scenarios**.

---

## Verified Research Resources

Detailed paper tracking:

- [`docs/literature-review/paper-table.md`](docs/literature-review/paper-table.md)

Verified dataset links and source notes:

- [`docs/literature-review/datasets.md`](docs/literature-review/datasets.md)

### Highest-priority papers

1. [A Comprehensive Review of Pill Image Recognition](https://doi.org/10.32604/cmc.2025.060793)
2. [High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion](https://doi.org/10.1371/journal.pone.0291865)
3. [ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification](https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html)
4. [Few-Shot Pill Recognition](https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html)
5. [Design and Validation of a Cyber-Physical Medication Dispensing Platform Integrating Edge AI Verification, Distributed Control, and Cloud Synchronization](https://doi.org/10.3390/s26123823)
6. [Code-Based Versus AutoML Methods for Pill Recognition in Clinical Settings: Comparative Performance Study](https://doi.org/10.2196/79160)

### Verified datasets

#### VAIPE — primary candidate

- Associated paper: https://doi.org/10.1371/journal.pone.0291865
- Public dataset linked by the paper: https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset
- VinUniversity Smart Health resource page: https://smarthealth.vinuni.edu.vn/resources/

#### ePillID

- Paper: https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html
- Official benchmark repository: https://github.com/usuyama/ePillID-benchmark

#### CURE

- Paper: https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html
- Author repository / data instructions: https://github.com/suiyiling/Few-shot-pill-recognition

#### NLM C3PI / RxIMAGE

- Official U.S. government dataset page: https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi
- Challenge paper: https://doi.org/10.1109/AIPR.2016.8010584

---

## Primary Dataset Direction

The current primary candidate is **VAIPE**, because it is particularly relevant to the proposed research problem. It supports multi-pill recognition and is associated with prescription/context information, making it more suitable for medication-verification research than a standard single-pill classification dataset.

Before training, the project will explicitly verify:

- annotation format
- exact class mapping
- dataset split
- prescription/context fields
- licensing / usage terms
- whether context information covers the full dataset or only a subset

Secondary datasets such as ePillID, CURE, and NLM C3PI will only be introduced if they answer a specific research need such as fine-grained recognition, low-shot learning, or auxiliary pretraining.

---

## Proposed Research Workflow

```text
Literature Review
       ↓
Problem Definition
       ↓
Dataset Selection & Exploration
       ↓
Baseline Multi-Pill Detector
       ↓
Detection Error Analysis
       ↓
Prescription-Matching Baseline
       ↓
Synthetic Dispensing-Error Generator
       ↓
Verification Experiments
       ↓
Robustness / Model Comparison
       ↓
Prescription-Aware Method Development
       ↓
Ablation & Error Analysis
       ↓
Final Evaluation
       ↓
Report & Presentation
```

---

## Planned Experiments

| Experiment | Description | Status |
| --- | --- | --- |
| `EXP-001` | Baseline multi-pill detection on the selected public dataset | Planned |
| `EXP-002` | Prescription-to-detection matching baseline | Planned |
| `EXP-003` | Simulated missing / extra / wrong-pill error detection | Planned |
| `EXP-004` | Model and confidence-threshold comparison | Planned |
| `EXP-005` | Robustness analysis: occlusion, density, lighting, similar pills | Planned |
| `EXP-006` | Prescription-aware verification method | Tentative |

Each experiment should record:

- Research hypothesis
- Dataset and split
- Model and weights
- Training configuration
- Evaluation metrics
- Random seed where applicable
- Hardware and software environment
- Results
- Failure cases
- Interpretation
- Conclusion

---

## Evaluation Metrics

### Object detection

- Precision
- Recall
- mAP@0.5
- mAP@0.5:0.95
- Per-class AP
- Inference latency

### Medication verification

- Verification accuracy
- Dispensing-error detection rate
- False Acceptance Rate (FAR)
- False Rejection Rate (FRR)
- Missing-pill detection rate
- Extra-pill detection rate
- Wrong-pill detection rate

For this project, **False Acceptance Rate is especially important** because a false acceptance means an incorrect medication set is incorrectly classified as valid.

---

## Simulated Dispensing Errors

A key part of the project is to evaluate the verification layer without requiring access to real hospital dispensing errors.

Given an expected prescription such as:

```text
Drug A × 2
Drug B × 1
Drug C × 1
```

reproducible test cases can be generated programmatically:

```text
Correct       A A B C
Missing       A B C
Extra         A A A B C
Wrong pill    A A B D
Multiple      A B D
```

This allows large-scale controlled experiments while keeping the project reproducible and independent of private patient data.

---

## Semester 1 Timeline

The first semester focuses on literature review, public-dataset validation, baselines, and formulation of the final research method.

| Week | Main Task | Status |
| --- | --- | --- |
| 01 | Research pivot, problem formulation, repository restructuring | 🔄 |
| 02 | Review core medication-verification papers and inspect VAIPE | ⬜ |
| 03 | Dataset pipeline and exploratory analysis | ⬜ |
| 04 | Baseline multi-pill detection (`EXP-001`) | ⬜ |
| 05 | Baseline evaluation and failure-case analysis | ⬜ |
| 06 | Prescription representation and matching pipeline | ⬜ |
| 07 | Prescription-verification baseline (`EXP-002`) | ⬜ |
| 08 | Synthetic dispensing-error generator | ⬜ |
| 09 | Error-detection experiment (`EXP-003`) | ⬜ |
| 10 | Compare models / confidence thresholds (`EXP-004`) | ⬜ |
| 11 | Robustness experiment design | ⬜ |
| 12 | Robustness experiments (`EXP-005`) | ⬜ |
| 13 | Research-gap review and final method selection | ⬜ |
| 14 | Implement prescription-aware method v1 | ⬜ |
| 15 | Initial proposed-method experiment | ⬜ |
| 16 | Results consolidation and visualization | ⬜ |
| 17 | Semester report preparation | ⬜ |
| 18 | Semester presentation and Semester 2 plan | ⬜ |

---

## Semester 2 Timeline

| Week | Main Task | Status |
| --- | --- | --- |
| 01 | Review Semester 1 findings and finalize research question | ⬜ |
| 02 | Refine proposed method | ⬜ |
| 03 | Implementation | ⬜ |
| 04 | Implementation and debugging | ⬜ |
| 05 | Main experiment setup | ⬜ |
| 06 | Main experiments | ⬜ |
| 07 | Main experiments | ⬜ |
| 08 | Parameter tuning | ⬜ |
| 09 | Comparison experiments | ⬜ |
| 10 | Comparison experiments | ⬜ |
| 11 | Ablation study | ⬜ |
| 12 | Safety-oriented verification evaluation | ⬜ |
| 13 | Error and failure-case analysis | ⬜ |
| 14 | Result visualization | ⬜ |
| 15 | Final report writing | ⬜ |
| 16 | Final report writing | ⬜ |
| 17 | Demo and presentation preparation | ⬜ |
| 18 | Final presentation | ⬜ |

---

## Repository Structure

```text
special_project/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── project-scope.md
│   ├── weekly-logs/
│   │   ├── semester-1/
│   │   └── semester-2/
│   ├── literature-review/
│   │   ├── paper-table.md
│   │   └── datasets.md
│   └── meetings/
│
├── experiments/
├── src/
├── notebooks/
├── results/
└── configs/
```

---

## Literature Review Strategy

The first literature-review stage targets approximately **15 core papers**. The verified reading list is maintained in:

[`docs/literature-review/paper-table.md`](docs/literature-review/paper-table.md)

The final thesis bibliography is expected to expand beyond these initial core papers as the methodology and experimental design become more specific.

---

## Possible Technologies

The project may use:

- Python
- PyTorch
- Ultralytics YOLO
- RT-DETR or another comparison detector
- OpenCV
- NumPy
- Pandas
- Matplotlib
- Jupyter / Kaggle
- CUDA
- Git / GitHub

The technology stack is intentionally flexible during the literature-review and baseline stage.

---

## Current Progress

**Semester:** 1  
**Current Week:** Week 01 / 18

Current stage:

```text
Research Pivot
      ↓
Literature Review
      ↓
Dataset Feasibility Validation
```

### Current priorities

- [x] Preserve the existing Special Project repository and research history
- [x] Pivot the repository from UAV detection to medication verification
- [x] Define the tentative research question and scope
- [x] Replace placeholder literature entries with verified paper links
- [x] Add verified public dataset sources
- [ ] Read the first group of core papers
- [ ] Inspect VAIPE annotations, prescriptions, and train/test structure
- [ ] Confirm dataset licensing and reproducibility
- [ ] Build a small dataset-loading notebook
- [ ] Run the first baseline detection test
- [ ] Discuss the revised direction with the advisor

---

## Research Pivot Note

The project initially explored **small-object detection in UAV imagery**. During the early problem-formulation stage, the direction was changed to medication verification because the new topic offers a clearer application scenario and a stronger system-level research question for the capstone.

The earlier UAV exploration remains part of the repository history, but all new experiments should follow the medication-verification research direction unless another change is explicitly documented.

---

## Important Note

This repository documents an **ongoing academic research project**. The final research question, datasets, models, and experimental protocol may change based on literature findings, advisor feedback, dataset feasibility, and experimental evidence.

This project is a research prototype and is **not intended for clinical use**.

---

## Project Status

🚧 **Work in Progress — Semester 1, Week 01**
