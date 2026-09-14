# UAV Small Object Detection

## Overview

This repository contains the development progress of my undergraduate Special Project / Capstone Project.

The project is a **6-credit research project conducted over one academic year**, including:

* Semester 1: 3 credits, 18 weeks
* Semester 2: 3 credits, 18 weeks
* Total duration: 36 weeks

The current research direction focuses on **small object detection in UAV imagery**, particularly investigating techniques that can improve detection performance for small and densely distributed objects.

---

## Tentative Research Topic

**Improving Small Object Detection in UAV Imagery Using Adaptive Image Tiling and Multi-Scale Training**

The topic may be refined during the literature review and early experimentation stages.

---

## Research Motivation

Object detection in UAV imagery is more challenging than conventional object detection because objects are often:

* Very small relative to the image resolution
* Densely distributed
* Captured from different altitudes
* Affected by scale variation
* Partially occluded
* Surrounded by complex backgrounds

When high-resolution UAV images are resized before being passed into an object detection model, small objects may lose important visual information.

This project investigates methods such as:

* Image tiling
* Adaptive image slicing
* Multi-scale training
* Small-object data augmentation
* Modern object detection architectures
* Improved inference strategies

to improve the detection performance of small objects.

---

## Project Objectives

The main objectives of this project are:

1. Study existing research related to small object detection in UAV imagery.
2. Select suitable UAV object detection datasets.
3. Establish a baseline object detection model.
4. Analyze common failure cases of the baseline model.
5. Implement image tiling and multi-scale training strategies.
6. Compare different approaches through controlled experiments.
7. Evaluate the proposed method using standard object detection metrics.
8. Document the research process and experimental results.

---

## Research Workflow

The general research workflow is:

```text
Literature Review
       ↓
Problem Definition
       ↓
Dataset Selection
       ↓
Baseline Implementation
       ↓
Baseline Evaluation
       ↓
Error Analysis
       ↓
Method Development
       ↓
Experiments
       ↓
Comparison & Ablation Study
       ↓
Final Evaluation
       ↓
Report & Presentation
```

---

## Project Timeline

### Semester 1

Literature review and implementation will run in parallel so that the research
direction is supported by reproducible experimental evidence from the beginning.

| Week | Main Task                                                        | Status |
| ---- | ---------------------------------------------------------------- | ------ |
| 01   | Project setup, core paper search, and pretrained YOLO smoke test | 🔄     |
| 02   | VisDrone exploration and YOLO baseline training (`EXP-001`)      | ⬜      |
| 03   | SAHI fixed-tiling reproduction and comparison (`EXP-002`)        | ⬜      |
| 04   | Baseline error analysis and research-question refinement         | ⬜      |
| 05   | Study adaptive-tiling methods and define evaluation protocol      | ⬜      |
| 06   | Design adaptive-tiling method v1                                 | ⬜      |
| 07   | Implement adaptive-tiling method v1                              | ⬜      |
| 08   | Debug and validate adaptive-tiling pipeline                       | ⬜      |
| 09   | Initial adaptive-tiling experiment (`EXP-003`)                    | ⬜      |
| 10   | Multi-scale training experiment (`EXP-004`)                       | ⬜      |
| 11   | Combined-method experiment (`EXP-005`)                            | ⬜      |
| 12   | Accuracy-efficiency comparison                                   | ⬜      |
| 13   | Ablation study and parameter analysis                            | ⬜      |
| 14   | Failure-case analysis                                            | ⬜      |
| 15   | Method refinement and final Semester 1 experiments               | ⬜      |
| 16   | Results consolidation and visualization                          | ⬜      |
| 17   | Semester report preparation                                      | ⬜      |
| 18   | Semester presentation and next-semester plan                     | ⬜      |

### Semester 2

| Week | Main Task                         | Status |
| ---- | --------------------------------- | ------ |
| 01   | Review previous semester results  | ⬜      |
| 02   | Finalize proposed method          | ⬜      |
| 03   | Method implementation             | ⬜      |
| 04   | Method implementation             | ⬜      |
| 05   | Initial experiment                | ⬜      |
| 06   | Main experiments                  | ⬜      |
| 07   | Main experiments                  | ⬜      |
| 08   | Parameter tuning                  | ⬜      |
| 09   | Comparison experiments            | ⬜      |
| 10   | Comparison experiments            | ⬜      |
| 11   | Ablation study                    | ⬜      |
| 12   | Performance evaluation            | ⬜      |
| 13   | Error analysis                    | ⬜      |
| 14   | Result visualization              | ⬜      |
| 15   | Final report writing              | ⬜      |
| 16   | Final report writing              | ⬜      |
| 17   | Presentation and demo preparation | ⬜      |
| 18   | Final presentation                | ⬜      |

---

## Repository Structure

```text
UAV-Small-Object-Detection/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── weekly-logs/
│   │   ├── semester-1/
│   │   └── semester-2/
│   │
│   ├── literature-review/
│   └── meetings/
│
├── experiments/
├── src/
├── notebooks/
├── results/
└── configs/
```

### `docs/weekly-logs`

Contains weekly research progress.

Each weekly log records:

* Goals
* Work completed
* Papers read
* Experiments performed
* Problems encountered
* What I learned
* Advisor feedback
* Plan for the following week

### `docs/literature-review`

Contains notes and summaries of research papers related to the project.

### `docs/meetings`

Contains meeting notes and feedback from the project advisor.

### `experiments`

Contains experiment configurations, results, and analysis.

Each experiment should have a unique ID, for example:

```text
EXP-001-baseline
EXP-002-image-tiling
EXP-003-multi-scale-training
```

### `src`

Contains the main project source code.

### `notebooks`

Contains Jupyter notebooks used for:

* Dataset exploration
* Visualization
* Experimental analysis

### `results`

Contains figures, result tables, prediction samples, and other outputs used in reports.

### `configs`

Contains model and experiment configuration files.

---

## Weekly Documentation

Research progress will be documented every week.

Example:

```text
docs/
└── weekly-logs/
    ├── semester-1/
    │   ├── week-01.md
    │   ├── week-02.md
    │   └── ...
    │
    └── semester-2/
        ├── week-01.md
        ├── week-02.md
        └── ...
```

The purpose of weekly documentation is to preserve the complete development history of the project.

The general research cycle is:

```text
Paper
  ↓
Idea
  ↓
Implementation
  ↓
Experiment
  ↓
Result
  ↓
Analysis
  ↓
Next Experiment
```

---

## Experiment Tracking

Experiments will be recorded using unique experiment IDs.

Example:

| Experiment | Description                     | Status  |
| ---------- | ------------------------------- | ------- |
| EXP-001    | Baseline object detection model | Planned |
| EXP-002    | Fixed image tiling              | Planned |
| EXP-003    | Adaptive image tiling           | Planned |
| EXP-004    | Multi-scale training            | Planned |
| EXP-005    | Tiling + multi-scale training   | Planned |

Each experiment should record:

* Research hypothesis
* Model
* Dataset
* Training configuration
* Evaluation metrics
* Results
* Observations
* Conclusion

---

## Evaluation Metrics

The project may use standard object detection metrics such as:

* Precision
* Recall
* mAP@0.5
* mAP@0.5:0.95
* AP for small objects
* Inference time
* Computational cost

Additional metrics may be included depending on the selected dataset and experimental design.

---

## Possible Datasets

Potential UAV datasets to investigate include:

* VisDrone
* UAVDT
* DOTA
* xView
* Other UAV or aerial imagery datasets

The final dataset will be selected after evaluating its suitability for the research problem.

---

## Possible Technologies

The project may use:

* Python
* PyTorch
* Ultralytics YOLO
* OpenCV
* NumPy
* Pandas
* Matplotlib
* Jupyter Notebook
* CUDA
* Git / GitHub

The technology stack may change as the project develops.

---

## Literature Review

Research papers will mainly focus on:

* Small Object Detection
* UAV Object Detection
* Aerial Image Object Detection
* Image Tiling
* Image Slicing
* Multi-Scale Training
* Feature Pyramid Networks
* YOLO-based Object Detection
* Transformer-based Object Detection

Paper notes will be stored under:

```text
docs/literature-review/
```

---

## Current Progress

**Semester:** 1
**Current Week:** Week 01 / 18

Current stage:

```text
Project Setup → Literature Review + Pretrained Inference Smoke Test
```

### Week 01

Current tasks:

* [x] Create GitHub repository
* [x] Create project directory structure
* [x] Initialize Git repository
* [x] Create project README
* [x] Define tentative research scope
* [x] Create the initial core-paper reading list
* [ ] Set up the Python environment
* [ ] Read the VisDrone paper and skim the FPN, YOLO9000, and SAHI papers
* [ ] Download several VisDrone sample images
* [ ] Run pretrained YOLO inference on the sample images
* [ ] Save prediction samples and record observations
* [ ] Discuss research direction with advisor

Detailed Week 01 tasks and notes are recorded in
[`docs/weekly-logs/semester-1/week-01.md`](docs/weekly-logs/semester-1/week-01.md).

---

## Important Note

This repository documents an ongoing research project.

The research topic, methodology, datasets, models, and experimental design may change based on:

* Literature review findings
* Experimental results
* Advisor feedback
* Available computational resources
* Research feasibility

Changes to the research direction will be documented in the weekly logs.

---

## Project Status

🚧 **Work in Progress**

Semester 1 — Week 01
