# Dataset Resources

This file tracks **real, traceable dataset sources** for the medication-verification project.

The goal is to distinguish:

- original / official sources
- paper-associated downloads
- mirrors or derivative repositories

Do not treat a random re-upload as the canonical source unless the original source is unavailable.

---

## 1. VAIPE — Primary Dataset Candidate

### Why it is important

VAIPE is currently the strongest candidate for this project because it was designed for **real-world multi-pill recognition** and is linked to prescription/context information.

Relevant paper:

- **High accurate and explainable multi-pill detection framework with graph neural network-assisted multimodal data fusion**
- PLOS ONE, 2023
- DOI: https://doi.org/10.1371/journal.pone.0291865

### Dataset download

The paper's Data Availability section points to a public Kaggle release:

- **VAIPE minimal dataset**  
  https://www.kaggle.com/datasets/anhduy091100/vaipe-minimal-dataset

### Additional project/resource page

VinUniversity Smart Health resource page:

- https://smarthealth.vinuni.edu.vn/resources/

### Intended use in this project

- multi-pill object detection
- medication classification
- medication counting
- prescription/context-aware verification
- robustness analysis

### Important checks before training

- inspect exact annotation format
- verify class count and class mapping
- confirm train/validation/test organization
- inspect prescription-linked metadata
- check license / redistribution terms on the download page
- verify whether every image has prescription/context information or only a subset

---

## 2. ePillID

### Paper

- **ePillID Dataset: A Low-Shot Fine-Grained Benchmark for Pill Identification**
- CVPR Workshops 2020
- Paper: https://openaccess.thecvf.com/content_CVPRW_2020/html/w54/Usuyama_ePillID_Dataset_A_Low-Shot_Fine-Grained_Benchmark_for_Pill_Identification_CVPRW_2020_paper.html

### Official benchmark repository

- https://github.com/usuyama/ePillID-benchmark

The repository contains benchmark information and dataset-access instructions.

### Why it is useful

- fine-grained pill identification
- visually similar pill classes
- low-shot / few-shot evaluation
- reference-image vs consumer-image matching

### Role in this project

Likely a **secondary dataset**, useful for studying visually similar medications or as an auxiliary recognition benchmark rather than the main multi-pill verification dataset.

---

## 3. CURE — Few-Shot Pill Recognition Dataset

### Paper

- **Few-Shot Pill Recognition**
- CVPR 2020
- Paper: https://openaccess.thecvf.com/content_CVPR_2020/html/Ling_Few-Shot_Pill_Recognition_CVPR_2020_paper.html

### Author repository

- https://github.com/suiyiling/Few-shot-pill-recognition

The repository contains code and dataset-download information associated with the paper.

### Why it is useful

- few-shot recognition
- difficult fine-grained pill classes
- varied imaging conditions
- comparison with ePillID-style identification tasks

### Role in this project

Secondary benchmark for fine-grained recognition and generalization experiments.

---

## 4. NLM C3PI / RxIMAGE

### Official project/data source

U.S. government Data.gov entry for the National Library of Medicine's **Computational Photography Project for Pill Identification (C3PI)**:

- https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi

### Related challenge paper

- **The National Library of Medicine Pill Image Recognition Challenge: An Initial Report**
- DOI: https://doi.org/10.1109/AIPR.2016.8010584

### Why it is useful

Historically one of the major pill-identification image resources. It is useful for:

- reference pill images
- consumer-quality pill images
- pill-image retrieval / identification research
- pretraining or auxiliary experiments

### Important limitation

The C3PI project is historical and is **not a current clinical drug database**. Drug identifiers or metadata should not be treated as current prescribing information.

Use it as a **computer-vision research dataset**, not as an authoritative medication database.

---

## 5. VAIPE-PCIL

### Paper

- **Multi-stream Fusion for Class Incremental Learning in Pill Image Classification**
- ACCV 2022
- Paper: https://openaccess.thecvf.com/content/ACCV2022/html/Nguyen_Multi-stream_Fusion_for_Class_Incremental_Learning_in_Pill_Image_Classification_ACCV_2022_paper.html

### Code / dataset repository

- https://github.com/vinuni-vishc/CG-IMIF

### Why it is useful

The dataset/repository is relevant if the project later studies **class-incremental learning**, i.e. adding new medication classes without retraining from scratch.

This is not necessary for the first baseline.

---

# Dataset Selection Recommendation

## Primary

**VAIPE**

Use it first because the project is focused on:

```text
multiple pills
+
context / prescription information
+
verification
```

## Secondary

**ePillID / CURE**

Use these if the project needs deeper analysis of:

- visually similar medications
- few-shot recognition
- low-shot generalization

## Auxiliary

**NLM C3PI / RxIMAGE**

Potential use:

- auxiliary pretraining
- historical benchmark comparison
- image retrieval experiments

---

# What Not to Do

Do not combine datasets immediately just because more images appear better.

Different datasets may have incompatible:

- medication identifiers
- image domains
- annotation formats
- label definitions
- class taxonomies
- licensing terms

First reproduce a clean baseline on **one primary dataset**.

Recommended order:

```text
VAIPE inspection
      ↓
VAIPE baseline
      ↓
verification experiment
      ↓
identify limitation
      ↓
only then decide whether another dataset is needed
```

---

# Dataset Verification Checklist

Before using any dataset in an experiment, record:

```text
Dataset name:
Original source:
Associated paper:
Download URL:
License / terms:
Number of images:
Number of classes:
Single-pill or multi-pill:
Annotation format:
Prescription/context data available?:
Official train/val/test split?:
Known limitations:
Date accessed:
```

This information should later be included in the methodology section of the final report.
