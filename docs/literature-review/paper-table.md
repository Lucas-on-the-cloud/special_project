# Literature Review Tracker

Tentative topic:

**Prescription-Aware Multi-Pill Detection and Verification for Smart Medication Dispensing Systems**

This file contains the first **15 verified core papers** for the project. Links point to DOI/publisher pages, CVF Open Access, PubMed/JMIR, or other primary publication sources whenever possible.

> The 15 papers below are the initial core reading set, not the final thesis bibliography.

---

## 15 Core Papers

| # | Paper | Year | Category | Why it matters for this project | Data / code | Status |
|---:|---|---:|---|---|---|---|
| 1 | [A Comprehensive Review of Pill Image Recognition](https://doi.org/10.32604/cmc.2025.060793) | 2025 | Review | Best starting map of pill-recognition methods, public datasets, limitations, and open problems | Reviews NLM, ePillID, CURE, VAIPE, VAIPE-PCIL | Not started |
| 2 | [High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion](https://doi.org/10.1371/journal.pone.0291865) | 2023 | Multi-pill detection / VAIPE | **Most important paper for this project.** Detects multiple pills in real-world images and uses prescription/co-occurrence context | [VAIPE minimal dataset](https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset) | Not started |
| 3 | [ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification](https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html) | 2020 | Dataset / fine-grained recognition | Important benchmark for visually similar pills and low-shot learning | [Official benchmark repo](https://github.com/usuyama/ePillID-benchmark) | Not started |
| 4 | [Few-Shot Pill Recognition](https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html) | 2020 | Dataset / few-shot recognition | Introduces CURE and studies difficult pill-recognition cases under varied imaging conditions | [Author repo + CURE download](https://github.com/suiyiling/Few-shot-pill-recognition) | Not started |
| 5 | [The National Library of Medicine Pill Image Recognition Challenge: An Initial Report](https://doi.org/10.1109/AIPR.2016.8010584) | 2016/2017 | Benchmark / dataset history | Defines the NLM challenge and reference-vs-consumer pill image retrieval problem | [C3PI / RxIMAGE official data page](https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi) | Not started |
| 6 | [Development of fine-grained pill identification algorithm using deep convolutional network](https://doi.org/10.1016/j.jbi.2017.09.005) | 2017 | Fine-grained recognition | Early deep-learning pill identification work; useful historical baseline and problem formulation | Paper datasets | Not started |
| 7 | [An Accurate Deep Learning-Based System for Automatic Pill Identification: Model Development and Validation](https://doi.org/10.2196/41043) | 2023 | Pill identification / retrieval | Combines visual pill features and imprint information; useful for handling similar-looking pills | Uses open Korean/US pill databases | Not started |
| 8 | [Effects of Background Colors, Flashes, and Exposure Values on the Accuracy of a Smartphone-Based Pill Recognition System Using a Deep Convolutional Neural Network](https://doi.org/10.2196/26000) | 2021 | Robustness / real-world imaging | Directly supports experiments on lighting, background, flash, and capture-condition robustness | Experimental image data in study | Not started |
| 9 | [Multi-stream Fusion for Class Incremental Learning in Pill Image Classification](https://openaccess.thecvf.com/content/ACCV2022/html/Nguyen_Multi-stream_Fusion_for_Class_Incremental_Learning_in_Pill_Image_Classification_ACCV_2022_paper.html) | 2022 | Continual learning / VAIPE | Addresses new pill classes and uses VAIPE-PCIL; relevant because medication classes change over time | [Code + VAIPE-PCIL](https://github.com/vinuni-vishc/CG-IMIF) | Not started |
| 10 | [Enhanced Multi-Pill Detection and Recognition Using VFI Augmentation and Auto-Labeling for Limited Single-Pill Data](https://doi.org/10.1109/ACCESS.2025.3557569) | 2025 | Multi-pill detection | Recent multi-pill detection paper; useful comparison for augmentation and limited-data settings | See paper | Not started |
| 11 | [Code-Based Versus AutoML Methods for Pill Recognition in Clinical Settings: Comparative Performance Study](https://doi.org/10.2196/79160) | 2026 | Clinical / real-world evaluation | Evaluates YOLO11 and AutoML across multiple real clinical environments; very useful for generalization discussion | Clinical datasets are not all public | Not started |
| 12 | [A hybrid framework for pill identification using convolutional neural networks and optical character recognition](https://doi.org/10.1007/s44163-026-01405-x) | 2026 | CNN + OCR | Shows how visual features and pill imprints can be combined; uses several public datasets | C3PI, ePillID and other public sets | Not started |
| 13 | [Design and Validation of a Cyber-Physical Medication Dispensing Platform Integrating Edge AI Verification, Distributed Control, and Cloud Synchronization](https://doi.org/10.3390/s26123823) | 2026 | Smart dispensing / AI verification | **Closest end-to-end system paper**: robotic dispensing + YOLOv8 visual verification + edge AI + cloud | Custom controlled dataset | Not started |
| 14 | [Design and Implementation of a Smart Medication Dispensing System with Visual and Weight-Based Verification for Patient Safety](https://doi.org/10.1109/ELECO69582.2025.11329260) | 2025 | Smart dispensing / multimodal verification | Verifies medication type and quantity using both vision and weight | Custom prototype data | Not started |
| 15 | [A Vision-Guided, IoT-Integrated Pill Dispensing System for Intelligent Medication Adherence](https://doi.org/10.1109/EDCT65302.2025.11495984) | 2025 | Smart dispensing / IoT | Useful system-level comparison for vision, embedded hardware, IoT, and medication adherence | Prototype study | Not started |

---

## Optional Recent Paper

This paper is newer than the initial list and may be useful after the 15 core papers:

- [A lightweight hybrid deep learning framework for multi-pill detection, multi-attribute recognition, OCR-based imprint analysis, and metadata retrieval](https://doi.org/10.3389/frai.2026.1890296) — Frontiers in Artificial Intelligence, 2026.

It combines multi-pill detection, classification, OCR, and metadata retrieval in one pipeline.

---

## Recommended Reading Order

Do **not** read the papers simply from #1 to #15. A more efficient order is:

### Stage A — Understand the field

1. **Paper #1 — Review**
2. **Paper #2 — VAIPE / PGPNet**
3. **Paper #13 — Cyber-physical smart dispenser**

After these three papers, the project problem and application should be much clearer.

### Stage B — Understand available datasets

4. **Paper #3 — ePillID**
5. **Paper #4 — CURE**
6. **Paper #5 — NLM challenge**
7. Read [`datasets.md`](datasets.md)

### Stage C — Understand recognition difficulties

8. **Paper #6 — fine-grained recognition**
9. **Paper #7 — visual + imprint recognition**
10. **Paper #8 — lighting/background robustness**
11. **Paper #9 — new pill classes / continual learning**

### Stage D — Understand current systems and modern baselines

12. **Paper #10 — recent multi-pill detection**
13. **Paper #11 — YOLO11 clinical evaluation**
14. **Paper #12 — CNN + OCR hybrid**
15. **Papers #14 and #15 — dispensing-system architecture**

---

## Highest-Priority Papers for the Proposal

If there is only time to read **six papers carefully** before discussing the project with the advisor, prioritize:

1. VAIPE / PGPNet (#2)
2. Pill Recognition Review (#1)
3. Cyber-Physical Medication Dispensing Platform (#13)
4. ePillID (#3)
5. Few-Shot Pill Recognition / CURE (#4)
6. Clinical YOLO11 study (#11)

---

## Key Dataset References

Dataset download links and source-quality notes are maintained separately in:

[`datasets.md`](datasets.md)

This is intentional: dataset mirrors, licenses, and official download pages can change independently of the papers.

---

## Detailed Review Table

Fill this table while reading. Do not copy abstracts; summarize in your own words.

| Paper | Exact task | Dataset | Main method | Metrics | Key result | Failure cases | Reproducible with public data? | Useful idea / gap |
|---|---|---|---|---|---|---|---|---|
| #1 Review |  |  |  |  |  |  |  |  |
| #2 VAIPE / PGPNet |  |  |  |  |  |  |  |  |
| #3 ePillID |  |  |  |  |  |  |  |  |
| #4 CURE |  |  |  |  |  |  |  |  |
| #5 NLM Challenge |  |  |  |  |  |  |  |  |
| #6 Fine-grained DCN |  |  |  |  |  |  |  |  |
| #7 Automatic Pill ID |  |  |  |  |  |  |  |  |
| #8 Capture Robustness |  |  |  |  |  |  |  |  |
| #9 VAIPE-PCIL |  |  |  |  |  |  |  |  |
| #10 Multi-Pill + VFI |  |  |  |  |  |  |  |  |
| #11 Clinical YOLO11 / AutoML |  |  |  |  |  |  |  |  |
| #12 CNN + OCR |  |  |  |  |  |  |  |  |
| #13 Edge-AI Dispenser |  |  |  |  |  |  |  |  |
| #14 Vision + Weight Dispenser |  |  |  |  |  |  |  |  |
| #15 Vision + IoT Dispenser |  |  |  |  |  |  |  |  |

---

## Questions to Answer for Every Paper

1. What exact task is solved: classification, detection, retrieval, counting, verification, OCR, or end-to-end dispensing?
2. Is the dataset public?
3. How many images/classes are used?
4. Are images single-pill or multi-pill?
5. Are prescriptions or other contextual data available?
6. What model is used?
7. What metrics are reported?
8. What happens with visually similar pills?
9. What happens with occlusion, lighting changes, or clutter?
10. Does the study measure dangerous false acceptance / false-negative cases?
11. Can the experiment be reproduced without real patient data?
12. What limitation could become a research gap for this capstone?

---

## Literature Review Goal

The review should support this chain:

```text
Existing pill-recognition research
            ↓
Public datasets and reproducible baselines
            ↓
Existing dispensing / verification systems
            ↓
Known limitations and safety-critical errors
            ↓
Research gap
            ↓
Prescription-aware verification question
            ↓
Experimental design
```

The intended contribution should **not** be merely “use YOLO to recognize pills.” The stronger direction is **prescription-aware multi-pill verification and dispensing-error detection**.
