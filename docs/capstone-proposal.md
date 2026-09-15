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
3. Build a baseline multi-pill detection model.
4. Build a prescription-matching module that compares expected and detected medication sets.
5. Develop a controlled simulation framework for common dispensing errors.
6. Evaluate the complete verification pipeline using both computer-vision and safety-oriented metrics.
7. Analyze failure cases and robustness under difficult visual conditions.
8. Explore a prescription-aware method in which structured prescription information helps constrain or improve visual predictions.
9. Produce a reproducible research prototype, final report, and demonstration.

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

## 6. Datasets

The project will rely on public datasets because access to real hospital dispensing data is not available.

### 6.1 Primary dataset: VAIPE

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

### 6.2 Secondary datasets

#### ePillID

Paper:  
https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html

Official benchmark repository:  
https://github.com/usuyama/ePillID-benchmark

Potential use: fine-grained recognition and visually similar pill classes.

#### CURE

Paper:  
https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html

Author repository:  
https://github.com/suiyiling/Few-shot-pill-recognition

Potential use: few-shot recognition and auxiliary comparison.

#### NLM / C3PI / RxIMAGE

Official government resource page:  
https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi

Potential use: auxiliary reference images, historical benchmark comparison, or pretraining.

These datasets will be evaluated for licensing, annotation format, class balance, and compatibility before final use.

---

## 7. Proposed Methodology

### Phase 1 — Literature Review and Dataset Validation

The first stage will study approximately 15 core papers covering:

- pill recognition,
- fine-grained pill identification,
- multi-pill detection,
- smart dispensing systems,
- clinical robustness,
- medication verification,
- relevant public datasets.

The literature review will be used to define the final research gap and baseline models.

### Phase 2 — Baseline Multi-Pill Detection

A baseline object-detection model will be trained or fine-tuned on the selected public dataset.

Candidate models include:

- YOLO11,
- another YOLO variant where appropriate,
- RT-DETR or another detector for comparison.

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

The system will then classify the event as:

```text
MATCH
```

or

```text
MISMATCH
```

and explain which medication is missing, extra, or incorrect.

### Phase 4 — Simulated Dispensing Errors

Since real dispensing-error data is difficult to obtain, controlled error scenarios will be generated programmatically.

For example:

```text
Expected:    A A B C
Correct:     A A B C
Missing:     A B C
Extra:       A A A B C
Wrong pill:  A A B D
Multiple:    A B D
```

This allows thousands of reproducible verification trials to be generated without collecting private patient data.

### Phase 5 — Robustness Evaluation

The system will be evaluated under difficult visual conditions such as:

- pill overlap,
- occlusion,
- high pill density,
- visually similar medications,
- lighting variation,
- background variation,
- different confidence thresholds.

### Phase 6 — Prescription-Aware Verification

After establishing a baseline, the project will explore whether prescription context can improve performance.

For example, if the visual model assigns similar probabilities to several visually similar medications, the prescription may provide a constrained candidate set.

This stage is intended to investigate whether a **prescription-aware model** can reduce unsafe verification errors compared with a vision-only baseline.

---

## 8. Experimental Plan

| Experiment | Description |
|---|---|
| EXP-001 | Baseline multi-pill detection |
| EXP-002 | Prescription-to-detection matching baseline |
| EXP-003 | Simulated missing / extra / wrong-pill detection |
| EXP-004 | Model and confidence-threshold comparison |
| EXP-005 | Robustness analysis under difficult visual conditions |
| EXP-006 | Prescription-aware verification method |

Each experiment will record:

- hypothesis,
- dataset and split,
- model configuration,
- random seed,
- hardware/software environment,
- evaluation metrics,
- quantitative results,
- failure cases,
- conclusions.

---

## 9. Evaluation Metrics

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

## 10. Expected Contribution

The project does not aim to claim a new pill-recognition problem. Instead, the intended contribution is a reproducible framework that connects three components:

```text
Multi-pill visual perception
          +
Electronic prescription context
          +
Safety-oriented dispensing verification
```

The expected contribution is therefore:

1. a reproducible public-dataset-based verification pipeline,
2. a controlled dispensing-error simulation framework,
3. a safety-oriented evaluation protocol,
4. an analysis of when vision-based medication verification fails,
5. an exploratory prescription-aware method for reducing verification errors.

---

## 11. Feasibility

The project is considered feasible for an undergraduate capstone because:

- public datasets already exist,
- the experiments do not require private hospital data,
- the core task can be implemented using standard computer-vision frameworks,
- training can be performed using Kaggle or university GPU resources,
- the project can be completed as a software research prototype even without constructing a full physical medication dispenser.

If time permits, a small simulated dispensing interface or hardware demonstration may be added, but the research contribution will remain centered on the AI verification pipeline.

---

## 12. Risks and Mitigation

### Risk 1 — Dataset access or annotation limitations

**Mitigation:** evaluate VAIPE first and keep ePillID, CURE, and NLM/C3PI as secondary resources.

### Risk 2 — Too many visually similar classes

**Mitigation:** begin with a controlled subset of classes, then scale up gradually.

### Risk 3 — Detection accuracy is insufficient for verification

**Mitigation:** perform per-class and failure-case analysis, tune thresholds, compare detectors, and test prescription-aware constraints.

### Risk 4 — Project becomes only a system integration project

**Mitigation:** keep the research question centered on measurable verification reliability, error detection, and false acceptance rather than only building a dispenser interface.

### Risk 5 — Project scope becomes too large

**Mitigation:** prioritize the software verification pipeline first. Hardware is optional.

---

## 13. Tentative Timeline

### Semester 1

| Week | Main Task |
|---|---|
| 1 | Explore research topics, pivot from UAV detection, define medication-verification direction |
| 2 | Read core papers and inspect VAIPE |
| 3 | Dataset pipeline and exploratory analysis |
| 4 | Baseline multi-pill detection |
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

The second semester will focus on method refinement, larger experiments, ablation studies, error analysis, report writing, and final presentation.

---

## 14. Initial Core References

1. **A Comprehensive Review of Pill Image Recognition** (2025)  
   https://doi.org/10.32604/cmc.2025.060793

2. **High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion** (2023)  
   https://doi.org/10.1371/journal.pone.0291865

3. **ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification** (2020)  
   https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html

4. **Few-Shot Pill Recognition** (2020)  
   https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html

5. **Design and Validation of a Cyber-Physical Medication Dispensing Platform Integrating Edge AI Verification, Distributed Control, and Cloud Synchronization** (2026)  
   https://doi.org/10.3390/s26123823

6. **Code-Based Versus AutoML Methods for Pill Recognition in Clinical Settings: Comparative Performance Study** (2026)  
   https://doi.org/10.2196/79160

A larger literature tracker is maintained in:

[`docs/literature-review/paper-table.md`](literature-review/paper-table.md)

---

## 15. Current Status

The project is currently at the **topic exploration and feasibility-validation stage**.

Week 1 has been used to:

- explore an initial UAV object-detection topic,
- evaluate its application relevance,
- identify a stronger medication-verification problem,
- review the available pill-recognition research landscape,
- identify public datasets,
- formulate a tentative research question,
- define the first experimental roadmap.

The next immediate step is to validate VAIPE in detail and determine whether its prescription information can directly support the proposed verification experiments.
