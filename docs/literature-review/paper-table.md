# Literature Review Tracker

This table tracks the papers most relevant to the tentative topic:

**Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

The initial goal is to identify approximately **15 core papers** that define the research problem, available datasets, existing medication-recognition methods, smart dispensing systems, and evaluation strategies.

---

## Reading Strategy

The first literature-review set should contain approximately:

| Category | Target |
| --- | ---: |
| Survey / review papers | 2 |
| Pill detection / recognition | 4 |
| Dataset / benchmark papers | 3 |
| Smart dispensing / medication verification | 3 |
| Clinical or real-world AI medication studies | 2 |
| Main model / methodology paper | 1 |
| **Total** | **15** |

These 15 papers are the **core reading set**, not the final thesis bibliography.

---

## Current Reading Priority

| Priority | Paper / Resource | Year | Role in this project | Reading plan | Status |
| --- | --- | ---: | --- | --- | --- |
| 1 | **High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion (VAIPE)** | 2023 | Most relevant public multi-pill dataset and prescription-linked benchmark | Very careful read | Not started |
| 2 | **A Comprehensive Review of Pill Image Recognition** | 2025 | Survey of major pill-recognition datasets, methods, and open problems | Careful read | Not started |
| 3 | **ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification** | 2020 | Fine-grained / low-shot pill-identification benchmark | Careful read | Not started |
| 4 | **Few-Shot Pill Recognition (CURE)** | 2020 | Few-shot recognition benchmark and dataset | Careful read | Not started |
| 5 | **Design and Validation of a Cyber–Physical Medication Dispensing Platform Integrating Edge AI Verification, Distributed Control, and Cloud Synchronization** | 2026 | Very close smart-dispensing + visual-verification system | Very careful read | Not started |
| 6 | **Design and Implementation of a Smart Medication Dispensing System with Visual and Weight-Based Verification for Patient Safety** | 2025 | Relevant end-to-end medication verification architecture | Careful read | Not started |
| 7 | **Vision-Guided, IoT-Integrated Pill Dispensing System** | 2025 | Vision + embedded / IoT dispensing reference | Main concepts | Not started |
| 8 | **NLM / C3PI / RxIMAGE resource documentation** | — | Large-scale pill-image source and historical benchmark context | Dataset review | Not started |
| 9 | **Recent clinical multi-pill / medication-recognition study** | TBD | Real-world validation and failure modes | To select | Not started |
| 10 | **Recent pill detection / recognition paper using YOLO** | TBD | Modern baseline comparison | To select | Not started |
| 11 | **Recent transformer-based medication-recognition paper** | TBD | Alternative detector / recognizer | To select | Not started |
| 12 | **Medication dispensing error / patient-safety study** | TBD | Defines practical error types and safety motivation | To select | Not started |
| 13 | **Prescription-aware or multimodal medication recognition paper** | TBD | Directly relevant to RQ4 | To select | Not started |
| 14 | **Confidence calibration / safety-critical vision paper** | TBD | Helps analyze false acceptance and confidence thresholds | To select | Not started |
| 15 | **Final model-method paper used by the project** | TBD | Technical reference for the selected detector | To select | Not started |

---

## Key Dataset References

### VAIPE

Current primary dataset candidate.

Relevant characteristics to verify during reading:

- Multi-pill images
- Bounding-box annotations
- Medication class labels
- Prescription-linked information
- Multiple backgrounds / lighting conditions
- Suitability for object detection and prescription verification

Paper:
https://pmc.ncbi.nlm.nih.gov/articles/PMC10538799/

### ePillID

Useful for fine-grained and low-shot pill identification.

Repository:
https://github.com/usuyama/ePillID-benchmark

### CURE

Useful for few-shot pill recognition and comparison with ePillID.

### NLM / C3PI / RxIMAGE

Potentially useful as an auxiliary large-scale pill-image source. Historical medication identifiers must not be interpreted as a current clinical drug database.

---

## Detailed Review Table

Fill one row after reading each paper. Use your own words and record exact section, table, or figure numbers for results that may later be cited.

| Paper | Problem | Main method | Dataset | Metrics / key result | Code / data | Limitation | Useful for this project? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VAIPE | TBD | TBD | VAIPE | TBD | TBD | TBD | Primary dataset + multi-pill detection |
| Pill Recognition Review | TBD | Survey | Multiple | TBD | N/A | TBD | Research landscape and gaps |
| ePillID | TBD | Low-shot fine-grained recognition | ePillID | TBD | Yes | TBD | Fine-grained recognition reference |
| CURE | TBD | Few-shot pill recognition | CURE | TBD | TBD | TBD | Dataset / recognition comparison |
| Edge-AI Smart Dispenser | TBD | Visual verification + cyber-physical system | Custom | TBD | TBD | Custom physical setup | Closest system-level related work |
| Visual + Weight Verification | TBD | Vision + weight checking | Custom | TBD | TBD | TBD | Verification-system reference |

---

## Questions to Answer While Reading

For every important paper, try to answer:

1. What exact problem is the paper solving?
2. Is the task classification, detection, retrieval, counting, verification, or full-system integration?
3. What dataset is used and is it publicly available?
4. How many pill classes and images are included?
5. Are images single-pill or multi-pill?
6. Does the dataset include prescription information?
7. What model is used?
8. Which metrics are reported?
9. What are the most common failure cases?
10. Does the paper evaluate visually similar pills, occlusion, lighting, or pill density?
11. Does it measure false acceptance of incorrect medication?
12. What part can be reproduced without access to hospital or patient data?
13. What limitation could become a research gap for this project?

---

## Reading Notes Template

For each core paper, create a separate note when more detail is needed:

```text
Citation:
Year / Venue:
Research problem:
Why the problem matters:
Task type:
Main idea:
Method / pipeline:
Dataset:
Number of classes / images:
Public dataset?:
Experimental setup:
Metrics:
Key results:
Failure cases:
Limitations:
What can be reproduced:
How it relates to this project:
Potential research gap:
Questions:
```

---

## Literature Review Goal

The literature review should eventually support the following chain:

```text
Existing pill-recognition research
            ↓
Available public datasets
            ↓
Existing smart dispensing / verification systems
            ↓
Known limitations and safety risks
            ↓
Research gap
            ↓
Research question
            ↓
Experimental design
```

The project should avoid making its contribution simply **"using YOLO to recognize pills"**, because pill recognition is already a well-established research problem. The stronger direction is to study **prescription-aware multi-pill verification and dispensing-error detection**.
