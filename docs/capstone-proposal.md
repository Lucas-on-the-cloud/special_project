# Capstone Project Proposal

## Title

**Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

## Student Project Type

Undergraduate Special Project / Capstone Project  
Duration: Two semesters (36 weeks)  
Credits: 6 credits total

---

## 1. Background and Motivation

Medication-dispensing systems are increasingly being automated through embedded systems, robotics, computer vision, and cloud-connected platforms. In a typical smart-dispensing workflow, a patient is first authenticated through an insurance card, prescription number, QR code, or another digital identifier. The system then retrieves the medication order and releases the corresponding drugs.

However, a purely mechanical dispensing process does not by itself guarantee that the physical medication delivered to the patient exactly matches the electronic prescription. A dispensing error may still occur because of mechanical failure, incorrect container mapping, pill jamming, misclassification, or software integration errors.

For this reason, this project proposes an additional **AI-based visual verification layer**. Instead of allowing AI to diagnose a patient or generate a prescription, the AI module will perform a narrower and safer task: compare the medications visually detected after dispensing with the medications expected from an already-authorized electronic prescription.

The intended workflow is:

```text
Patient / Prescription ID
          ↓
Electronic Prescription
          ↓
Expected Medication List
          ↓
Medication Dispensing Process
          ↓
Image of Dispensed Pills
          ↓
Computer Vision Model
          ↓
Detected Medication + Quantity
          ↓
Expected vs Detected Comparison
          ↓
      MATCH / MISMATCH
```

The project therefore focuses on **medication verification**, not medical decision-making.

---

## 2. Problem Statement

Pill-recognition research has already shown that deep-learning models can identify or retrieve medications from images. Existing benchmarks such as ePillID, CURE, NLM/C3PI, and VAIPE provide data for fine-grained pill recognition, few-shot learning, and multi-pill detection.

However, a practical smart-dispensing system must answer a more safety-oriented question:

> **Does the medication physically dispensed match the medication that was prescribed?**

This is different from conventional pill classification because the system must verify both **medication identity and quantity**, and it must detect errors such as:

- missing medication,
- extra medication,
- incorrect medication,
- multiple simultaneous dispensing errors.

The project will investigate whether computer vision combined with prescription context can reliably detect these errors using only public datasets and reproducible simulated dispensing scenarios.

---

## 3. Main Research Question

> **How reliably can a vision-based medication verification system detect dispensing errors by comparing multi-pill detections with an electronic prescription?**

### Sub-questions

1. How accurately can modern object-detection models identify and count multiple pills in a single image?
2. How reliably can the system detect missing, extra, and incorrect medications?
3. How do occlusion, pill density, lighting, confidence threshold, and visually similar medications affect verification performance?
4. Can prescription information be used as contextual information to improve verification compared with vision-only prediction?

---

## 4. Project Objectives

The project aims to:

1. Review the existing literature on pill recognition, multi-pill detection, and smart medication-dispensing systems.
2. Select and validate suitable public datasets for reproducible experimentation.
3. Reproduce at least one published pill-recognition pipeline with public code and data to validate the research environment.
4. Build a baseline multi-pill detection model using a mature public framework.
5. Build a prescription-matching module that compares expected and detected medication sets.
6. Develop a controlled simulation framework for common dispensing errors.
7. Evaluate the complete verification pipeline using both computer-vision and safety-oriented metrics.
8. Analyze failure cases and robustness under difficult visual conditions.
9. Explore a prescription-aware method in which structured prescription information helps constrain or improve visual predictions.
10. Produce a reproducible research prototype, final report, and demonstration.

---

## 5. Scope

### In scope

- Public pill-image datasets
- Multi-pill object detection
- Pill classification and counting
- Prescription representation
- Prescription-to-image matching
- Simulated dispensing-error generation
- Model comparison
- Robustness experiments
- Error analysis
- Prototype verification API or dashboard

### Out of scope

- Disease diagnosis
- Treatment recommendation
- AI-generated prescriptions
- Real clinical deployment
- Testing with real patients
- Integration with a real hospital information system
- Medical-device certification

The project will be presented strictly as an **academic research prototype**.

---

## 6. Reproducibility Strategy

Because the project will be developed largely independently, implementation choices will prioritize **reproducibility and maintainability**.

The preferred order for implementation-related papers is:

```text
Official code + public dataset + runnable instructions
                        ↓
Official code + accessible dataset
                        ↓
Public dataset + standard maintained framework
                        ↓
Paper with no code
```

A paper without source code may still be important for motivation, system architecture, or research-gap analysis, but it will not automatically become the main reproduction target.

### Initial reproducible resources

#### ePillID

Paper:  
https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html

Official repository:  
https://github.com/usuyama/ePillID-benchmark

This repository provides public code, data access, environment instructions, and a tutorial workflow. It is a strong candidate for the first published baseline reproduction.

#### CG-IMIF / VAIPE-PCIL

Paper:  
https://openaccess.thecvf.com/content/ACCV2022/html/Nguyen_Multi-stream_Fusion_for_Class_Incremental_Learning_in_Pill_Image_Classification_ACCV_2022_paper.html

Official repository:  
https://github.com/vinuni-vishc/CG-IMIF

This project provides a second reproducible example within the VAIPE research ecosystem.

### Important implementation decision

The VAIPE / PGPNet paper is highly relevant to the capstone, but an official implementation of PGPNet has not been confirmed in the current review. Therefore, the project will initially use **VAIPE as the primary dataset while training a standard maintained detector such as Ultralytics YOLO**, instead of spending several weeks recreating PGPNet from scratch.

---

## 7. Datasets

The project will rely on public datasets because access to real hospital dispensing data is not available.

### 7.1 Primary dataset: VAIPE

The primary candidate is the VAIPE dataset introduced in:

**High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion**  
PLOS ONE, 2023  
DOI: https://doi.org/10.1371/journal.pone.0291865

VAIPE is particularly relevant because it contains:

- multi-pill images,
- pill-level annotations,
- multiple medication classes,
- images captured under varied real-world conditions,
- prescription-related contextual information.

Public dataset resource referenced by the paper:  
https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset

This structure makes VAIPE suitable for the planned pipeline:

```text
Prescription
     +
Multi-pill image
     ↓
Detection + counting
     ↓
Expected vs detected comparison
     ↓
MATCH / MISMATCH
```

### 7.2 Secondary datasets

#### ePillID

Official benchmark repository:  
https://github.com/usuyama/ePillID-benchmark

Potential use:

- first code reproduction,
- fine-grained recognition,
- visually similar pill classes.

#### CURE

Paper:  
https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html

Author repository:  
https://github.com/suiyiling/Few-shot-pill-recognition

Potential use: few-shot recognition and robustness comparison.

#### NLM / C3PI / RxIMAGE

Official government resource page:  
https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi

Potential use: auxiliary reference images, historical benchmark comparison, or pretraining.

These datasets will be evaluated for licensing, annotation format, class balance, and compatibility before final use.

---

## 8. Proposed Methodology

### Phase 1 — Literature Review, Code Review, and Dataset Validation

The first stage will study the core literature while explicitly checking:

- whether code is public,
- whether data are accessible,
- whether environment instructions are available,
- whether pretrained weights or evaluation scripts exist,
- whether the method can run on Kaggle/Colab or available GPU resources.

At least one published public-code baseline, most likely ePillID, will be reproduced before developing the final capstone pipeline.

### Phase 2 — Baseline Multi-Pill Detection

The primary baseline will use a mature, documented object-detection implementation.

Current first choice:

- **Ultralytics YOLO**

Possible comparison:

- RT-DETR or another public detector after the baseline is stable.

Each detected pill will be represented as:

```text
class label + bounding box + confidence score
```

### Phase 3 — Prescription Matching

The electronic prescription will be represented as a structured medication-count dictionary.

Example:

```text
Expected = {
    Drug_A: 2,
    Drug_B: 1,
    Drug_C: 1
}
```

The computer-vision output will be converted to the same format:

```text
Detected = {
    Drug_A: 2,
    Drug_B: 1,
    Drug_C: 1
}
```

The system will then classify the event as `MATCH` or `MISMATCH` and identify missing, extra, or unexpected medication.

### Phase 4 — Simulated Dispensing Errors

Controlled error scenarios will be generated programmatically:

```text
Expected:    A A B C
Correct:     A A B C
Missing:     A B C
Extra:       A A A B C
Wrong pill:  A A B D
Multiple:    A B D
```

This allows large-scale reproducible verification experiments without collecting private patient data.

### Phase 5 — Robustness Evaluation

The system will be evaluated under:

- pill overlap,
- occlusion,
- high pill density,
- visually similar medications,
- lighting variation,
- background variation,
- different confidence thresholds.

### Phase 6 — Prescription-Aware Verification

After the baseline is working, the project will explore whether prescription context can improve verification.

For example, the prescription may provide a constrained candidate set for ambiguous visual predictions.

---

## 9. Experimental Plan

| Experiment | Description |
|---|---|
| REP-001 | Reproduce a public-code pill-recognition baseline (ePillID preferred) |
| EXP-001 | Baseline multi-pill detection on VAIPE |
| EXP-002 | Prescription-to-detection matching baseline |
| EXP-003 | Simulated missing / extra / wrong-pill detection |
| EXP-004 | Model and confidence-threshold comparison |
| EXP-005 | Robustness analysis under difficult visual conditions |
| EXP-006 | Prescription-aware verification method |

Each experiment will record:

- hypothesis,
- repository / source commit where applicable,
- dataset and split,
- model configuration,
- dependency versions,
- random seed,
- hardware/software environment,
- evaluation metrics,
- quantitative results,
- failure cases,
- conclusions.

---

## 10. Evaluation Metrics

### Computer-vision metrics

- Precision
- Recall
- mAP@0.5
- mAP@0.5:0.95
- Per-class AP
- Inference latency

### Verification metrics

- Verification accuracy
- Dispensing-error detection rate
- False Acceptance Rate (FAR)
- False Rejection Rate (FRR)
- Missing-pill detection rate
- Extra-pill detection rate
- Wrong-pill detection rate

Particular attention will be paid to **False Acceptance Rate**, because a false acceptance means that an incorrect medication set is wrongly classified as valid.

---

## 11. Expected Contribution

The project does not aim to claim a new pill-recognition problem. Instead, the intended contribution is a reproducible framework connecting:

```text
Multi-pill visual perception
          +
Electronic prescription context
          +
Safety-oriented dispensing verification
```

Expected outputs include:

1. a reproducible public-dataset-based verification pipeline,
2. a controlled dispensing-error simulation framework,
3. a safety-oriented evaluation protocol,
4. an analysis of when vision-based medication verification fails,
5. an exploratory prescription-aware method for reducing verification errors.

---

## 12. Feasibility

The project is considered feasible because:

- public datasets exist,
- several related benchmarks have public code,
- the core implementation can use maintained computer-vision frameworks,
- no private patient data are required,
- Kaggle/Colab can be used for reproducible experiments,
- the project can remain software-based even without a physical dispenser.

If time permits, a simulated dispensing interface or hardware demonstration may be added.

---

## 13. Risks and Mitigation

### Risk 1 — Important paper has no code

**Mitigation:** use the paper for theory/background and reproduce a nearby method with public code instead. Do not spend several weeks recreating an undocumented implementation unless it becomes essential.

### Risk 2 — Dataset access or annotation limitations

**Mitigation:** evaluate VAIPE first and keep ePillID, CURE, and NLM/C3PI as secondary resources.

### Risk 3 — Too many visually similar classes

**Mitigation:** begin with a controlled subset of classes and scale up gradually.

### Risk 4 — Detection accuracy is insufficient

**Mitigation:** perform per-class analysis, tune thresholds, compare documented detectors, and test prescription-aware constraints.

### Risk 5 — Project becomes only system integration

**Mitigation:** center the research question on measurable verification reliability, error detection, and false acceptance.

### Risk 6 — Scope becomes too large

**Mitigation:** prioritize the software verification pipeline. Hardware remains optional.

---

## 14. Tentative Timeline

### Semester 1

| Week | Main Task |
|---|---|
| 1 | Explore research topics, pivot from UAV detection, define medication-verification direction |
| 2 | Read core papers, inspect code repositories, and inspect VAIPE |
| 3 | Reproduce one public-code pill-recognition baseline and build dataset pipeline |
| 4 | Baseline VAIPE multi-pill detection |
| 5 | Baseline evaluation and failure-case analysis |
| 6 | Prescription representation and matching module |
| 7 | Verification baseline |
| 8 | Simulated dispensing-error generator |
| 9 | Error-detection experiments |
| 10 | Model and threshold comparison |
| 11–12 | Robustness experiments |
| 13 | Research-gap review and method refinement |
| 14–15 | Prescription-aware method implementation and experiment |
| 16 | Result consolidation |
| 17 | Semester report |
| 18 | Presentation and Semester 2 planning |

### Semester 2

The second semester will focus on method refinement, larger experiments, ablation studies, error analysis, final report writing, and presentation.

---

## 15. Initial Core References

1. **A Comprehensive Review of Pill Image Recognition** (2025)  
   https://doi.org/10.32604/cmc.2025.060793

2. **High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion** (2023)  
   https://doi.org/10.1371/journal.pone.0291865

3. **ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification** (2020)  
   https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html  
   Code: https://github.com/usuyama/ePillID-benchmark

4. **Few-Shot Pill Recognition** (2020)  
   https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html  
   Data/repo: https://github.com/suiyiling/Few-shot-pill-recognition

5. **Multi-stream Fusion for Class Incremental Learning in Pill Image Classification** (2022)  
   https://openaccess.thecvf.com/content/ACCV2022/html/Nguyen_Multi-stream_Fusion_for_Class_Incremental_Learning_in_Pill_Image_Classification_ACCV_2022_paper.html  
   Code: https://github.com/vinuni-vishc/CG-IMIF

6. **Design and Validation of a Cyber-Physical Medication Dispensing Platform Integrating Edge AI Verification, Distributed Control, and Cloud Synchronization** (2026)  
   https://doi.org/10.3390/s26123823

Detailed literature and reproducibility tracking:

- [`docs/literature-review/paper-table.md`](literature-review/paper-table.md)
- [`docs/literature-review/reproducibility-priority.md`](literature-review/reproducibility-priority.md)

---

## 16. Current Status

The project is currently at the **topic exploration and feasibility-validation stage**.

Week 1 has been used to:

- explore an initial UAV object-detection topic,
- evaluate its application relevance,
- identify a stronger medication-verification problem,
- review the pill-recognition research landscape,
- identify public datasets,
- identify reproducible paper/code resources,
- formulate a tentative research question,
- define the first experimental roadmap.

The next immediate step is to inspect VAIPE in detail and reproduce at least one public-code pill-recognition baseline before beginning the main VAIPE detector experiments.
