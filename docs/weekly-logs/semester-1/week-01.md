# Semester 1 — Week 01

**Period:** 2026-09-14 to 2026-09-20  
**Stage:** Research pivot, problem formulation, and literature orientation

## Weekly Goal

Refine the Special Project direction and establish a research problem that is both practically meaningful and feasible using public datasets.

The project initially explored **small-object detection in UAV imagery**. After early investigation, the direction was changed to **AI-assisted medication verification for smart prescription dispensing** because the new topic provides a clearer application scenario and a stronger system-level research question.

The current tentative topic is:

> **Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

---

## Success Criteria

- [x] Preserve the existing repository and research history.
- [x] Document the research pivot clearly.
- [x] Define a new tentative topic and research questions.
- [x] Identify public medication-image datasets suitable for experimentation.
- [x] Identify an initial set of core papers and related systems.
- [ ] Read and summarize the first 4–5 core papers.
- [ ] Inspect the VAIPE dataset structure and annotations.
- [ ] Verify dataset licensing and reproducibility.
- [ ] Discuss the revised direction with the project advisor.

---

## Research Pivot

### Previous direction

**Improving Small Object Detection in UAV Imagery Using Adaptive Image Tiling and Multi-Scale Training**

The UAV direction was useful for learning the research workflow, object-detection pipeline, Kaggle environment, and YOLO inference. However, the application focus was not sufficiently compelling for the intended capstone direction.

### New direction

**AI-Assisted Medication Verification for Smart Prescription Dispensing**

The new research idea is to compare:

```text
Expected medication from an electronic prescription
                     ↓
              Verification
                     ↑
Medication detected from an image of dispensed pills
```

The AI component acts as an independent **verification layer** rather than making medical decisions.

---

## Tentative Research Question

> **How reliably can a vision-based medication verification system detect dispensing errors by comparing multi-pill detections with an electronic prescription?**

Possible sub-questions:

1. How accurately can object-detection models identify and count multiple pills?
2. How reliably can the system detect missing, extra, and wrong medication?
3. How do lighting, occlusion, pill density, and visually similar pills affect verification accuracy?
4. Can prescription information be used as contextual information to reduce visual-recognition errors?

---

## Dataset Feasibility

The project should be feasible without collecting real patient or hospital data.

### Primary candidate: VAIPE

VAIPE is currently the strongest dataset candidate because it contains multi-pill imagery, pill annotations, and prescription-related information.

This makes it directly relevant to the intended pipeline:

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

### Additional datasets to investigate

- ePillID
- CURE
- NLM / RxIMAGE / C3PI

These datasets may be useful for fine-grained recognition, auxiliary experiments, or model pretraining.

---

## Literature Review Plan

The initial literature review will target approximately **15 core papers**:

- 2 survey / review papers
- 4 pill detection / recognition papers
- 3 dataset / benchmark papers
- 3 smart dispensing / medication-verification papers
- 2 clinical or real-world medication-AI studies
- 1 main model / methodology paper

The detailed tracker is maintained in:

[`docs/literature-review/paper-table.md`](../../literature-review/paper-table.md)

---

## Planned Experimental Direction

### EXP-001 — Baseline multi-pill detection

Train or fine-tune a baseline detector on the selected public dataset.

Candidate metrics:

- Precision
- Recall
- mAP@0.5
- mAP@0.5:0.95
- Per-class AP
- Inference latency

### EXP-002 — Prescription matching baseline

Convert the expected prescription and detected pills into structured medication counts and determine whether they match.

### EXP-003 — Simulated dispensing errors

Programmatically create controlled scenarios such as:

```text
Expected: A A B C

Correct:    A A B C
Missing:    A B C
Extra:      A A A B C
Wrong pill: A A B D
Multiple:   A B D
```

Evaluate whether the verification system identifies each error type.

Potential safety-oriented metrics:

- Verification accuracy
- False Acceptance Rate
- False Rejection Rate
- Missing-pill detection rate
- Extra-pill detection rate
- Wrong-pill detection rate

---

## Previous UAV Work Completed

Before the research pivot, the following exploratory work was completed:

- Repository structure created.
- Kaggle environment configured.
- VisDrone2019-DET validation data downloaded.
- COCO-pretrained YOLO11n inference run on eight UAV images.
- Prediction samples and metadata exported.
- Basic failure cases in small-object UAV detection observed.

This work is retained as part of the research history, but it will not be continued unless specifically required later.

---

## What I Learned

### From the UAV exploration

- A research topic should not be selected only because a model or dataset is technically interesting.
- The application context and research question need to be clear enough to justify the experiments.
- A pretrained inference smoke test is useful for validating the development environment before committing to a research direction.

### From the medication-verification investigation

- Pill recognition already has substantial prior research, so simply training YOLO to identify pills would be a weak contribution.
- A stronger direction is **prescription-aware verification**, where vision predictions are evaluated in the context of an expected prescription.
- Public datasets make it possible to design reproducible experiments without collecting real patient data.
- False acceptance of incorrect medication should be treated as an especially important failure mode.

---

## Advisor Feedback

- No feedback recorded yet.

---

## Plan for Week 02

1. Read the VAIPE paper carefully.
2. Read one recent pill-recognition review paper.
3. Read the ePillID and CURE benchmark papers.
4. Read at least one recent smart medication-dispenser / AI-verification system paper.
5. Inspect the VAIPE dataset structure and annotation format.
6. Verify whether prescription information is directly usable for the planned experiments.
7. Create a small exploratory notebook for dataset loading and visualization.
8. Refine the final research question based on the literature findings.
9. Discuss the revised topic and feasibility with the advisor.

---

## Weekly Summary

The first week began with an exploration of UAV small-object detection, including a reproducible Kaggle environment and a YOLO inference smoke test. During problem formulation, the project direction was reconsidered because the intended application and contribution were not sufficiently clear. The new tentative direction is AI-assisted medication verification for smart prescription dispensing. Initial literature and dataset investigation indicates that public datasets such as VAIPE may allow the project to study multi-pill detection and prescription-based verification without requiring real patient data. The project will therefore focus next on literature review, dataset validation, and formulation of a reproducible dispensing-error experiment. The immediate priority for Week 02 is to determine whether VAIPE can support the proposed end-to-end verification pipeline.
