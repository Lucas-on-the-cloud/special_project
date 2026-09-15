# Semester 1 — Week 01 Progress Report

**Period:** 2026-09-14 to 2026-09-20  
**Stage:** Topic exploration, research pivot, and feasibility validation

---

## 1. Weekly Objective

The main objective of Week 1 was **not to begin model training immediately**, but to identify a capstone topic that is:

- technically suitable for an Informatics project,
- meaningful in terms of real-world application,
- feasible with available public datasets,
- measurable through reproducible experiments,
- large enough for a two-semester capstone,
- but still realistic without access to private industry or hospital data.

The week therefore focused mainly on **research-topic exploration, problem formulation, literature scanning, and dataset feasibility**.

---

## 2. Initial Research Direction: UAV Small-Object Detection

The first tentative direction was:

> **Improving Small Object Detection in UAV Imagery Using Adaptive Image Tiling and Multi-Scale Training**

This direction was initially selected because UAV imagery provides a clear computer-vision challenge: objects are often small, densely distributed, partially occluded, and affected by large scale variation.

During the first exploration, I completed the following technical setup:

- created the GitHub repository and research folder structure,
- configured a Kaggle environment,
- downloaded the VisDrone2019-DET validation split,
- ran COCO-pretrained YOLO11n inference on eight UAV images,
- saved prediction results and runtime metadata,
- inspected common detection failures.

The smoke test confirmed that the development environment was functional and also showed several expected difficulties in UAV detection, especially missed distant pedestrians, motorcycles, bicycles, and small vehicles.

However, after considering the project from a capstone perspective, I became less confident about the application direction. Small-object detection in UAV imagery is an interesting research problem, but for this project I wanted a topic with a more concrete system-level application and a clearer connection between the AI component and an end-user problem.

This led to a deliberate research pivot rather than continuing with the first idea only because the initial code was already working.

---

## 3. Topic Exploration After the UAV Direction

The next step was to look for applications in which computer vision could perform a well-defined verification task instead of only improving a generic detection benchmark.

One idea that emerged was a **smart medication-dispensing system**.

The initial system concept was:

```text
Patient
   ↓
Insurance card / prescription number / QR code
   ↓
Retrieve electronic prescription
   ↓
Automatic dispensing
   ↓
Patient receives medication
```

At first, this idea was mainly an embedded/database/IoT system. The main question was therefore:

> Where can AI contribute in a way that is technically meaningful rather than being added artificially?

The most promising answer was to use AI **after dispensing**, as an independent visual verification layer.

The resulting concept became:

```text
Electronic Prescription
        ↓
Expected Medication List
        ↓
Dispensed Pills
        ↓
Camera
        ↓
Computer Vision Model
        ↓
Detected Medication + Quantity
        ↓
Expected vs Detected
        ↓
MATCH / MISMATCH
```

This changed the topic from simply building a smart dispenser to studying **AI-assisted medication verification**.

---

## 4. New Tentative Research Direction

The current tentative title is:

> **Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

Alternative working title:

> **AI-Assisted Medication Verification for Smart Prescription Dispensing**

The AI component is intentionally limited to **verification**.

The project will not attempt to:

- diagnose disease,
- recommend treatment,
- generate prescriptions,
- replace pharmacists or clinicians.

Instead, the research focuses on whether the medications physically detected after dispensing correspond to an already-authorized prescription.

---

## 5. Tentative Research Question

The current main research question is:

> **How reliably can a vision-based medication verification system detect dispensing errors by comparing multi-pill detections with an electronic prescription?**

Potential sub-questions are:

1. How accurately can modern object-detection models identify and count multiple pills in one image?
2. How reliably can the system identify missing, extra, and incorrect medications?
3. How do occlusion, pill density, lighting, confidence thresholds, and visually similar pills affect verification performance?
4. Can prescription information be used as contextual information to improve verification compared with a vision-only model?

These questions are still tentative and will be refined after deeper reading and dataset inspection.

---

## 6. Literature Exploration

A major concern was whether this topic had enough prior research to support a capstone project while still leaving room for a meaningful research question.

The literature search showed that **pill recognition itself is already a well-established research area**. Therefore, simply training a YOLO model to classify pills would likely provide a weak research contribution.

Several major research directions were identified:

- fine-grained pill identification,
- low-shot and few-shot pill recognition,
- multi-pill detection,
- OCR-based imprint recognition,
- continual learning for new medication classes,
- robustness under different backgrounds and lighting conditions,
- smart medication-dispensing systems,
- visual medication verification.

This led to an important refinement:

> The contribution should not be “use AI to recognize pills.”

A stronger direction is:

> **Use multi-pill computer vision together with prescription information to verify whether the dispensed medication is correct.**

An initial set of approximately 15 core papers has now been identified and recorded in:

[`docs/literature-review/paper-table.md`](../../literature-review/paper-table.md)

The current highest-priority papers include:

1. **High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion** — VAIPE / PGPNet
2. **A Comprehensive Review of Pill Image Recognition**
3. **ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification**
4. **Few-Shot Pill Recognition** — CURE
5. **Design and Validation of a Cyber-Physical Medication Dispensing Platform Integrating Edge AI Verification, Distributed Control, and Cloud Synchronization**
6. **Code-Based Versus AutoML Methods for Pill Recognition in Clinical Settings: Comparative Performance Study**

---

## 7. Dataset Feasibility Exploration

A key feasibility question was whether the project could be completed without collecting real patient, prescription, or hospital data.

The literature search identified several relevant public resources.

### 7.1 VAIPE — Primary Candidate

The strongest current candidate is **VAIPE**.

Paper:

https://doi.org/10.1371/journal.pone.0291865

Dataset resource:

https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset

VAIPE is especially relevant because it includes:

- multi-pill images,
- pill annotations,
- multiple medication classes,
- varied image-capture conditions,
- prescription-related contextual information.

This makes it much closer to the planned research problem than a standard single-pill classification dataset.

### 7.2 ePillID

ePillID is useful for fine-grained recognition and visually similar pill classes.

Paper:

https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html

Repository:

https://github.com/usuyama/ePillID-benchmark

### 7.3 CURE

CURE is useful for few-shot pill recognition.

Paper:

https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html

Repository:

https://github.com/suiyiling/Few-shot-pill-recognition

### 7.4 NLM / C3PI / RxIMAGE

The NLM/C3PI resource provides a large historical pill-image collection that may be useful for auxiliary experiments or pretraining.

Official data resource:

https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi

A detailed dataset-source tracker is maintained in:

[`docs/literature-review/datasets.md`](../../literature-review/datasets.md)

---

## 8. Proposed Experimental Direction

After exploring the literature and available data, the project now has an initial experimental roadmap.

### EXP-001 — Baseline Multi-Pill Detection

Train or fine-tune a baseline detector on the selected public dataset.

Possible models:

- YOLO11,
- another YOLO baseline,
- RT-DETR or another detector for comparison.

Metrics:

- Precision
- Recall
- mAP@0.5
- mAP@0.5:0.95
- Per-class AP
- Inference latency

### EXP-002 — Prescription Matching Baseline

Represent both the electronic prescription and the detected medication set as structured medication counts.

Example:

```text
Expected = {A: 2, B: 1, C: 1}
Detected = {A: 2, B: 1, C: 1}
```

Then verify whether the two sets match.

### EXP-003 — Simulated Dispensing Errors

Because real dispensing-error data is difficult to obtain, controlled error cases can be generated programmatically.

Example:

```text
Expected:     A A B C

Correct:      A A B C
Missing:      A B C
Extra:        A A A B C
Wrong pill:   A A B D
Multiple:     A B D
```

This allows reproducible large-scale evaluation without private patient data.

### EXP-004 — Model and Threshold Comparison

Compare detection models and confidence thresholds to study the relationship between detection performance and verification safety.

### EXP-005 — Robustness Evaluation

Evaluate difficult cases such as:

- pill overlap,
- occlusion,
- high pill density,
- visually similar medications,
- lighting changes,
- background changes.

### EXP-006 — Prescription-Aware Verification

Explore whether prescription information can constrain candidate medication classes or otherwise improve verification compared with vision-only prediction.

---

## 9. Safety-Oriented Evaluation

In addition to normal computer-vision metrics, the project should evaluate the verification layer directly.

Candidate metrics include:

- Verification Accuracy
- Dispensing-Error Detection Rate
- False Acceptance Rate (FAR)
- False Rejection Rate (FRR)
- Missing-Pill Detection Rate
- Extra-Pill Detection Rate
- Wrong-Pill Detection Rate

Among these, **False Acceptance Rate** is especially important.

A false acceptance means:

```text
Incorrect medication set
        ↓
System says MATCH
```

This is more dangerous than a normal classification mistake and therefore should be analyzed separately.

---

## 10. Feasibility Assessment

At the end of Week 1, the new topic appears feasible for the following reasons:

1. Relevant public datasets already exist.
2. A full physical dispenser is not required to study the central research question.
3. The main experiments can be completed using public image data and simulated dispensing errors.
4. Computer-vision training can be performed on Kaggle or university GPU resources.
5. The research problem can be evaluated quantitatively.
6. The project combines AI, data processing, system logic, and application design without requiring sensitive patient data.
7. There is enough prior literature to support the project, but the prescription-verification angle provides a clearer research direction than generic pill classification.

---

## 11. Main Decisions Made This Week

- [x] Do not continue the UAV topic only because the initial pipeline already works.
- [x] Pivot toward a problem with a clearer practical application.
- [x] Use AI as a **verification layer**, not as a clinical decision-maker.
- [x] Focus the research question on **dispensing error detection**.
- [x] Use public datasets rather than private clinical data.
- [x] Select VAIPE as the primary dataset candidate.
- [x] Maintain ePillID, CURE, and NLM/C3PI as secondary resources.
- [x] Build the literature review around approximately 15 core papers.
- [x] Define initial experiments before starting large-scale implementation.

---

## 12. What I Learned

### Research-process lessons

- A technically interesting task is not automatically a strong capstone topic.
- The application and research question should be evaluated before investing heavily in implementation.
- Running a small technical smoke test is useful, but the research direction should remain flexible during the exploration stage.
- Existing literature should be checked early to avoid proposing a contribution that has already been extensively studied.
- Dataset availability is a major factor in determining whether a research idea is realistically executable.

### Technical lessons

- Pill identification is a fine-grained recognition problem because many medications have very similar shape, color, and markings.
- Multi-pill detection is closer to the intended dispensing scenario than single-pill classification.
- Prescription context may provide useful information beyond visual appearance alone.
- Verification should be evaluated differently from ordinary classification because unsafe false acceptance is a critical failure case.

---

## 13. Problems / Open Questions

Several questions remain unresolved and will be investigated in Week 2:

1. How exactly is prescription information represented in VAIPE?
2. Can the VAIPE minimal dataset directly support prescription-to-image verification experiments?
3. How many medication classes are sufficiently represented for a reliable baseline?
4. Should the first baseline use full VAIPE or a controlled subset of classes?
5. Is object detection sufficient, or will detection + fine-grained classification be necessary?
6. Which verification metric should be treated as the primary project metric?
7. What is the strongest research gap after comparing recent multi-pill and smart-dispensing papers?

---

## 14. Advisor Feedback

No advisor feedback has been recorded yet for the revised direction.

The current proposal has been prepared for discussion with the advisor:

[`docs/capstone-proposal.md`](../../capstone-proposal.md)

---

## 15. Plan for Week 02

The Week 2 objectives are:

1. Read the VAIPE paper carefully.
2. Read the 2025 pill-recognition review paper.
3. Read the ePillID and CURE benchmark papers.
4. Read at least one recent smart medication-dispensing / AI-verification paper.
5. Download and inspect the VAIPE dataset.
6. Understand its folder structure, annotation format, pill classes, and prescription information.
7. Build a small exploratory notebook for image and annotation visualization.
8. Decide whether to use the full dataset or an initial subset.
9. Finalize the first baseline experiment (`EXP-001`).
10. Discuss the topic, scope, and feasibility with the advisor.

---

## 16. Week 01 Summary

Week 1 focused primarily on identifying a suitable research direction rather than immediately committing to model training. The project initially explored small-object detection in UAV imagery, and a complete YOLO inference smoke test was successfully performed on VisDrone data. However, after evaluating the broader application and potential research contribution, the UAV direction was reconsidered. A new idea involving smart medication dispensing was then explored, with the AI component reformulated as an independent visual verification layer rather than a prescribing or diagnostic system. Initial literature review showed that pill recognition is already an established field, which motivated a more specific research question around **prescription-aware multi-pill verification and dispensing-error detection**. Public datasets including VAIPE, ePillID, CURE, and NLM/C3PI were identified, with VAIPE currently considered the strongest primary dataset candidate. By the end of the week, the project had a tentative research question, a public-data strategy, an initial set of core papers, and a six-experiment roadmap. The highest-priority task for Week 2 is to validate whether VAIPE can support the proposed prescription-to-dispensed-medication verification pipeline.
