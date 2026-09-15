# Project Scope

## Working Title

**Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

## Core Idea

This project studies whether computer vision can act as a verification layer in a smart medication-dispensing workflow.

The intended logic is:

```text
Electronic prescription
        ↓
Expected medication set
        ↓
Dispensed medication image
        ↓
AI detection / recognition / counting
        ↓
Detected medication set
        ↓
Expected vs detected comparison
        ↓
MATCH / MISMATCH
```

The project does not attempt to diagnose disease, recommend treatment, or prescribe medication.

---

## Research Problem

Existing pill-recognition research shows that AI can identify medication images, but a smart dispensing system must answer a more safety-oriented question:

> **Does the medication physically dispensed match what was prescribed?**

This creates a verification problem involving both visual perception and structured prescription information.

---

## Current Research Question

> **How reliably can a vision-based medication verification system detect dispensing errors by comparing multi-pill detections with an electronic prescription?**

### Candidate sub-questions

1. How accurately can different detection models identify and count pills in multi-pill images?
2. How well can the system detect missing, extra, and incorrect medication?
3. Which conditions most strongly increase false acceptance: occlusion, density, confidence threshold, or visually similar pills?
4. Does using prescription context improve verification compared with vision-only prediction?

---

## Data Strategy

The project should be reproducible using public datasets rather than private hospital or patient data.

### Primary candidate

**VAIPE**

Reason:

- multi-pill imagery
- medication annotations
- prescription-linked information
- suitable for detection and verification experiments

### Secondary candidates

- ePillID
- CURE
- NLM / C3PI / RxIMAGE

These may support fine-grained recognition, auxiliary evaluation, or pretraining.

---

## Experimental Strategy

### Phase 1 — Perception baseline

Train or evaluate a baseline multi-pill detector.

Output:

```text
pill class + bounding box + confidence
```

### Phase 2 — Verification baseline

Convert both prescription and detections into medication-count dictionaries.

Example:

```text
Expected = {A: 2, B: 1, C: 1}
Detected = {A: 2, B: 1, C: 1}
```

Then classify the event as valid or invalid.

### Phase 3 — Controlled error simulation

Generate reproducible dispensing-error scenarios in software:

- missing medication
- extra medication
- wrong medication
- multiple simultaneous errors

### Phase 4 — Robustness evaluation

Evaluate performance under difficult cases such as:

- occlusion
- pill overlap
- high pill density
- visually similar pills
- lighting/background variation
- different confidence thresholds

### Phase 5 — Prescription-aware method

If supported by the literature and baseline results, develop a method that uses the prescription as contextual information to improve visual verification.

---

## Evaluation

### Vision metrics

- Precision
- Recall
- mAP@0.5
- mAP@0.5:0.95
- Per-class AP
- Inference latency

### Verification metrics

- Verification accuracy
- False Acceptance Rate (FAR)
- False Rejection Rate (FRR)
- Missing-pill detection rate
- Extra-pill detection rate
- Wrong-pill detection rate

The project should pay particular attention to **False Acceptance Rate**, because this corresponds to an incorrect medication set being incorrectly accepted as valid.

---

## Expected Deliverables

By the end of the project, the target outputs are:

1. A structured literature review.
2. A reproducible public-dataset pipeline.
3. A baseline multi-pill detector.
4. A prescription-matching verification module.
5. A dispensing-error simulation framework.
6. Comparative and robustness experiments.
7. Error analysis and ablation results.
8. A final research report.
9. A small demonstration interface or API if time permits.

---

## Explicit Non-Goals

This project will not claim:

- clinical readiness
- medical-device certification
- diagnostic capability
- treatment recommendation capability
- safe deployment without pharmacist / clinician validation

The output should be presented as an academic research prototype.
