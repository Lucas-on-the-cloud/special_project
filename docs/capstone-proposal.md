# Capstone Project Proposal

## Title

**Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

**Project type:** Undergraduate Special Project / Capstone Project  
**Duration:** Two semesters (36 weeks)  
**Credits:** 6 credits

---

## 1. Background and Motivation

Smart medication-dispensing systems can use a prescription number, QR code, insurance card, or another digital identifier to retrieve an authorized prescription and dispense the required medication. However, a mechanical dispensing process does not guarantee that the physical pills released by the system exactly match the electronic prescription. Errors may still occur because of incorrect container mapping, pill jamming, mechanical failure, or recognition errors.

This project proposes an **AI-based visual verification layer** for this workflow. The AI will not diagnose disease or generate prescriptions. Instead, it will identify and count the pills that have been dispensed, compare them with the expected medication list, and determine whether the dispensing event is correct.

```text
Electronic Prescription
        ↓
Expected Medication Set
        ↓
Dispensing Process
        ↓
Image of Dispensed Pills
        ↓
Computer Vision Model
        ↓
Detected Medication + Quantity
        ↓
Expected vs Detected
        ↓
MATCH / MISMATCH / UNCERTAIN
```

The project therefore focuses on **medication verification and dispensing-error detection**, rather than general pill classification alone.

---

## 2. Research Problem and Questions

Existing research has already demonstrated pill identification, fine-grained pill recognition, and multi-pill detection. Public benchmarks such as **ePillID, CURE, NLM/C3PI, and VAIPE** provide data for these tasks. However, a smart dispensing system must answer a more safety-oriented question:

> **Does the medication physically dispensed match what was prescribed?**

The main research question is:

> **How reliably can a vision-based medication verification system detect dispensing errors by comparing multi-pill detections with an electronic prescription?**

The project will investigate four sub-questions:

1. How accurately can a modern detector identify and count multiple pills in one image?
2. How reliably can the system detect missing, extra, and incorrect medication?
3. Which conditions cause the most dangerous verification failures, especially false acceptance of an incorrect medication set?
4. Can prescription context improve verification compared with a vision-only baseline?

---

## 3. Data and Reproducibility Strategy

The project will use **public datasets** so that the experiments can be reproduced without access to private patient or hospital data.

### Primary dataset: VAIPE

The main candidate is **VAIPE**, introduced in the 2023 PLOS ONE paper *High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion*.

VAIPE is especially suitable because it contains multi-pill images, pill annotations, varied capture conditions, and prescription-related contextual information.

- Paper: https://doi.org/10.1371/journal.pone.0291865
- Dataset: https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset

### Reproducible supporting resources

Implementation work will prioritize **public code + public data + runnable instructions**.

- **ePillID** — code and benchmark data: https://github.com/usuyama/ePillID-benchmark
- **CG-IMIF / VAIPE-PCIL** — official implementation in the VAIPE research ecosystem: https://github.com/vinuni-vishc/CG-IMIF
- **CURE** — author repository and dataset source: https://github.com/suiyiling/Few-shot-pill-recognition

A paper without code may still be used for background or system design, but it will not automatically become the main reproduction target.

---

## 4. Proposed Methodology

The project will follow the sequence **Read → Reproduce → Baseline → Error Analysis → Improve → Compare**.

### Stage 1 — Literature review and reproduction

Read the core pill-recognition and smart-dispensing papers and reproduce at least one public-code baseline, most likely ePillID. The goal is to validate the environment and understand the end-to-end research workflow before developing the main capstone system.

### Stage 2 — Baseline multi-pill detection

Train a standard, maintained detector on VAIPE. The first baseline will likely use **Ultralytics YOLO** because it is well documented and easy to reproduce on Kaggle/Colab. A second detector such as RT-DETR may be added later for comparison.

### Stage 3 — Prescription matching

Convert both the prescription and visual detections into structured medication counts.

```text
Expected = {A: 2, B: 1, C: 1}
Detected = {A: 2, B: 1, C: 1}
```

The verification module will return `MATCH`, `MISMATCH`, or potentially `UNCERTAIN`, together with the missing, extra, or unexpected medication.

### Stage 4 — Simulated dispensing errors

Because real hospital dispensing-error data are not available, controlled error cases will be generated programmatically:

```text
Correct:     A A B C
Missing:     A B C
Extra:       A A A B C
Wrong pill:  A A B D
Multiple:    A B D
```

This allows large-scale, reproducible safety evaluation without private medical data.

### Stage 5 — Error analysis and improvement

The improvement method will **not be selected in advance**. It will be chosen according to measured baseline failures.

Possible directions include:

- confidence calibration if incorrect predictions are overconfident;
- reject/abstain mechanisms for uncertain cases;
- supervised contrastive or metric learning for visually similar pills;
- prescription-based candidate filtering or reranking;
- set-based or graph-based context models if medication relationships prove useful.

Every additional method must be justified by an observed failure and compared with a simpler alternative.

---

## 5. Experimental Plan and Evaluation

| ID | Experiment |
|---|---|
| `REP-001` | Reproduce one public-code pill-recognition baseline |
| `EXP-001` | Baseline multi-pill detection on VAIPE |
| `EXP-002` | Prescription-to-detection matching baseline |
| `EXP-003` | Missing / extra / wrong-pill error simulation |
| `EXP-004` | Confidence-threshold and model comparison |
| `EXP-005` | Robustness analysis: occlusion, density, lighting, similar pills |
| `EXP-006` | Evidence-driven improvement method |

Computer-vision performance will be evaluated using **Precision, Recall, mAP@0.5, mAP@0.5:0.95, per-class AP, and inference latency**.

Verification performance will be evaluated using **verification accuracy, False Acceptance Rate (FAR), False Rejection Rate (FRR), and detection rates for missing, extra, and incorrect medication**.

FAR is particularly important because it represents a dangerous case where an incorrect medication set is wrongly accepted as valid.

---

## 6. Expected Contribution and Feasibility

The intended contribution is not simply “using YOLO to recognize pills.” The project aims to connect:

```text
Multi-pill visual detection
          +
Electronic prescription context
          +
Safety-oriented verification
```

Expected outputs are:

1. a reproducible public-dataset-based medication verification pipeline;
2. a controlled dispensing-error simulation framework;
3. a safety-oriented evaluation protocol centered on false acceptance;
4. a detailed failure analysis of vision-based medication verification;
5. an improvement method selected from the observed failure modes.

The project is feasible as an undergraduate capstone because public datasets and public code are available, no private patient data are required, and the main experiments can be performed using Kaggle/Colab or available GPU resources. A physical dispenser is optional; the core research contribution can be completed as a software prototype.

---

## 7. Tentative Schedule

**Semester 1:** literature review, code reproduction, VAIPE exploration, baseline detector, prescription matching, simulated error evaluation, failure analysis, and initial improvement method.

**Semester 2:** method refinement, comparison experiments, robustness tests, ablation study, final evaluation, report writing, and demonstration.

The immediate next step is to validate the VAIPE dataset in detail and reproduce one code-supported pill-recognition pipeline before starting the main baseline experiment.

---

## Key References

1. Nguyen et al., **High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion**, PLOS ONE, 2023.  
   https://doi.org/10.1371/journal.pone.0291865

2. Usuyama et al., **ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification**, CVPR Workshops, 2020.  
   https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html

3. Ling et al., **Few-Shot Pill Recognition**, CVPR, 2020.  
   https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html

4. Nguyen et al., **Multi-stream Fusion for Class Incremental Learning in Pill Image Classification**, ACCV, 2022.  
   https://openaccess.thecvf.com/content/ACCV2022/html/Nguyen_Multi-stream_Fusion_for_Class_Incremental_Learning_in_Pill_Image_Classification_ACCV_2022_paper.html

Detailed literature and methodology notes are maintained separately under `docs/literature-review/`.
