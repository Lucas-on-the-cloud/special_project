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

The tentative research questions are:

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

## Primary Dataset Direction

### VAIPE

The current primary candidate is the **VAIPE multi-pill dataset**, because it is particularly relevant to the proposed research problem.

It contains multi-pill images, pill annotations, and prescription-related information, making it suitable for studying the relationship between:

```text
Prescription
     +
Multi-pill Image
     ↓
Medication Verification
```

Reference:

- VAIPE paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC10538799/

### Secondary datasets

Additional datasets may be used for comparison, pretraining, or auxiliary experiments:

- **ePillID** — low-shot fine-grained pill identification  
  https://github.com/usuyama/ePillID-benchmark
- **CURE** — few-shot pill recognition benchmark
- **NLM / RxIMAGE / C3PI** — large-scale pill image resources for computer-vision research

The final dataset combination will be decided after examining licensing, labels, class balance, image format, and compatibility with the experimental design.

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
│   │   └── paper-table.md
│   └── meetings/
│
├── experiments/
├── src/
├── notebooks/
├── results/
└── configs/
```

### `docs/weekly-logs`

Contains weekly progress, including:

- Goals
- Work completed
- Papers read
- Experiments performed
- Problems encountered
- Advisor feedback
- Decisions and research pivots
- Plan for the following week

### `docs/literature-review`

Contains the core-paper tracker and detailed paper notes.

### `experiments`

Contains experiment configurations, outputs, and analyses. Large datasets and trained model weights should **not** be committed directly to GitHub.

### `src`

Contains reusable source code for dataset processing, detection, prescription matching, simulation, evaluation, and inference.

### `notebooks`

Used for dataset exploration, model prototyping, visualization, and experimental analysis.

### `results`

Contains selected figures, result tables, prediction examples, and report-ready outputs.

---

## Literature Review Strategy

The first literature-review stage targets approximately **15 core papers**, divided into:

- 2 survey / review papers
- 4 pill detection or recognition papers
- 3 dataset / benchmark papers
- 3 smart dispensing or medication-verification papers
- 2 recent clinical / real-world AI medication studies
- 1 main model / methodology paper

The final thesis bibliography is expected to expand beyond these initial core papers as the methodology and experimental design become more specific.

Paper notes are tracked in:

[`docs/literature-review/paper-table.md`](docs/literature-review/paper-table.md)

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
- [ ] Read the first group of core papers
- [ ] Inspect VAIPE annotations, prescriptions, and train/test structure
- [ ] Confirm dataset licensing and reproducibility
- [ ] Build a small dataset-loading notebook
- [ ] Run the first pretrained/baseline detection test
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
