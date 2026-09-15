# Improvement Methodology Roadmap

## Purpose

This document answers the question:

> After reproducing a baseline, **what methodology should be studied before proposing an improvement?**

The project should not improve the model by randomly adding modules. The preferred research workflow is:

```text
Read
  ↓
Reproduce
  ↓
Build project baseline
  ↓
Measure failures
  ↓
Identify dominant failure type
  ↓
Read the methodology related to that failure
  ↓
Form a hypothesis
  ↓
Implement the smallest reasonable improvement
  ↓
Compare against baseline
  ↓
Ablation + robustness analysis
```

The methods below are therefore **candidate tools**, not a checklist that must all be implemented.

---

# 1. Recommended Improvement Order

For this capstone, try improvements from the simplest and safest to the most complex:

```text
Baseline YOLO detector
        ↓
Confidence calibration
        ↓
Reject / abstain mechanism
        ↓
Prescription-aware rule baseline
        ↓
Failure-driven representation improvement
        ↓
Learned prescription-context fusion
        ↓
Graph / attention methods only if justified
```

The first improvement should usually **not** be a new large neural architecture.

---

# 2. Methodology Map

| Failure observed in baseline | Methodology to study | Priority | Difficulty |
|---|---|---:|---:|
| Model is overconfident on wrong pills | Confidence calibration | A | Low |
| Unsafe low-confidence cases should not be accepted | Selective prediction / reject option | A | Low–Medium |
| Visually similar pills are confused | Supervised contrastive / metric learning | A | Medium |
| Prescription information is not yet used | Simple prescription constraint / late fusion | A | Low |
| Prescription is an unordered set of medicines | Deep Sets / Set Transformer | B | Medium |
| Co-occurrence relationships between medicines matter | Graph Attention Networks | B | Medium–High |
| Classes are imbalanced / hard classes ignored | Focal Loss | B | Low |
| Performance degrades with occlusion/background changes | CutMix / Mixup | B | Low–Medium |

Priority A = likely useful for the core capstone.  
Priority B = use only if baseline error analysis supports it.

---

# 3. Confidence Calibration

## Why it matters

The system will probably use confidence thresholds to decide whether a medication prediction can be trusted.

A neural network can be **accurate but overconfident**, which is dangerous for this project because an incorrect high-confidence prediction can increase the **False Acceptance Rate (FAR)**.

Example:

```text
Prediction: Drug B
Confidence: 0.96
Ground truth: Drug A
```

If confidence values are poorly calibrated, a threshold such as `0.90` does not necessarily mean that the accepted predictions are approximately 90% reliable.

## Core paper

**On Calibration of Modern Neural Networks**  
Guo et al., ICML 2017

Paper:  
https://proceedings.mlr.press/v70/guo17a.html

Original demonstration code:  
https://github.com/gpleiss/temperature_scaling

Modern maintained implementation / metrics:  
https://github.com/probkit/probmetrics

## Method to start with

**Temperature Scaling**

Advantages:

- simple post-processing
- does not require retraining the detector
- easy ablation
- directly relevant to confidence thresholds

## Possible experiment

```text
YOLO confidence
      ↓
Temperature scaling
      ↓
Choose verification threshold
      ↓
Measure FAR / FRR / ECE
```

Compare:

| Method | ECE | FAR | FRR |
|---|---:|---:|---:|
| Raw confidence | TBD | TBD | TBD |
| Calibrated confidence | TBD | TBD | TBD |

### Recommendation

**Very high priority.** This is probably one of the first improvements to test because it is cheap and strongly connected to safety-oriented verification.

---

# 4. Selective Prediction / Reject Option

## Why it matters

For a medication-verification system, forcing the AI to always make a decision may be undesirable.

Instead:

```text
High confidence
    ↓
Automatic verification

Uncertain prediction
    ↓
REJECT / MANUAL REVIEW
```

This is usually called **selective prediction**, **classification with rejection**, or **abstention**.

## Core paper

**SelectiveNet: A Deep Neural Network with an Integrated Reject Option**  
Geifman & El-Yaniv, ICML 2019

Paper:  
https://proceedings.mlr.press/v97/geifman19a.html

Author code:  
https://github.com/geifmany/selectivenet

Earlier simpler selective-classification implementation:  
https://github.com/geifmany/selective_deep_learning

## Why it fits this capstone

A smart dispenser does not need to accept every AI prediction.

A more defensible system can output:

```text
MATCH
MISMATCH
UNCERTAIN → pharmacist/manual review
```

instead of only:

```text
MATCH
MISMATCH
```

## Possible experiment

Measure the trade-off between:

- coverage: percentage of cases automatically handled
- risk/error among automatically handled cases
- False Acceptance Rate

### Recommendation

**Very high priority after calibration.** A reject option may be more meaningful than trying to increase raw mAP by a tiny amount.

---

# 5. Supervised Contrastive Learning

## When to use it

Use this direction if error analysis shows many confusions between visually similar pills.

Example:

```text
Drug A: round, white, small
Drug B: round, white, small
```

Cross-entropy classification may not learn sufficiently discriminative embeddings.

Supervised contrastive learning explicitly encourages:

```text
same class → embeddings closer
other class → embeddings farther apart
```

## Core paper

**Supervised Contrastive Learning**  
Khosla et al., NeurIPS 2020

Paper:  
https://proceedings.neurips.cc/paper/2020/hash/d89a66c7c80a29b1bdbab0f2a1a94af8-Abstract.html

Reference PyTorch implementation:  
https://github.com/HobbitLong/SupContrast

## Possible use in this project

A two-stage system could be tested:

```text
YOLO
 ↓
Crop detected pill
 ↓
Embedding model
 ↓
Supervised contrastive representation
 ↓
Fine-grained pill class
```

Compare against the plain YOLO classification head.

### Recommendation

**High priority only if visually similar pills are an important baseline failure.**

---

# 6. Deep Metric Learning

## Why study it

Metric learning is closely related to supervised contrastive learning and is especially useful for fine-grained recognition and retrieval.

Instead of learning only a class boundary, the model learns a feature space in which visually/semantically similar examples are positioned appropriately.

## Practical methodology resource

**PyTorch Metric Learning**  
Musgrave, Belongie & Lim, 2020

Paper:  
https://arxiv.org/abs/2008.09164

Library / code:  
https://github.com/KevinMusgrave/pytorch-metric-learning

The library provides:

- contrastive loss
- triplet loss
- multi-similarity loss
- miners / hard-negative mining
- testers
- complete train/test workflows
- Colab examples

## Why it is useful for independent work

This library lets the project try metric-learning ideas without manually reimplementing every loss from a paper.

## Possible experiment

```text
Cross entropy baseline
        vs
Cross entropy + metric-learning loss
```

Evaluate especially on confusing pill pairs.

### Recommendation

Use as the **implementation toolbox** if the project chooses fine-grained embedding improvement.

---

# 7. Prescription Context as a Set — Deep Sets

## Why it matters

A prescription is naturally a **set**:

```text
{Drug A, Drug C, Drug F}
```

The order usually should not matter:

```text
[A, C, F]
[C, F, A]
```

should encode the same medication set.

## Core paper

**Deep Sets**  
Zaheer et al., NeurIPS 2017

Paper:  
https://arxiv.org/abs/1703.06114

Author code:  
https://github.com/manzilzaheer/DeepSets

## Possible project architecture

```text
Prescription drugs
      ↓
Deep Sets encoder
      ↓
Prescription embedding
               ↘
                 Fusion → pill verification
               ↗
Visual embedding
```

## Why this is attractive

Deep Sets is simpler than a graph neural network and respects the unordered nature of a prescription.

### Recommendation

**Preferred learned-context model before trying a GNN.**

---

# 8. Set Transformer

## Why study it

Deep Sets aggregates the set relatively simply. If interactions among prescription items appear important, an attention-based set encoder can model relationships between elements.

## Core paper

**Set Transformer: A Framework for Attention-based Permutation-Invariant Neural Networks**  
Lee et al., ICML 2019

Paper:  
https://proceedings.mlr.press/v97/lee19d.html

Author PyTorch implementation:  
https://github.com/juho-lee/set_transformer

## Possible project use

```text
Prescription set
      ↓
Set Transformer
      ↓
Context embedding
      +
Visual predictions
      ↓
Verification
```

### Recommendation

Try only after a simpler prescription-context baseline has been established.

---

# 9. Graph Attention Networks

## Why it may become relevant

The VAIPE/PGPNet research direction already suggests that relationships and co-occurrence between medicines can provide useful context.

If analysis shows that medicine co-occurrence information is important, medication classes can be represented as graph nodes and relationships as graph edges.

## Core paper

**Graph Attention Networks**  
Veličković et al., ICLR 2018

Paper:  
https://arxiv.org/abs/1710.10903

Author implementation:  
https://github.com/PetarV-/GAT

## Possible idea

```text
Medication co-occurrence graph
          ↓
Graph Attention Network
          ↓
Context-aware medication probabilities
          ↓
Visual verification
```

### Warning

Do **not** start here merely because GNN sounds novel.

A GNN should only be introduced if:

1. the baseline reveals context-related confusion,
2. simpler prescription constraints are insufficient,
3. the graph structure can be defined without leaking test information.

### Recommendation

**Optional advanced direction.**

---

# 10. Focal Loss

## When it helps

Use focal loss if the dataset has:

- strong class imbalance,
- many easy examples,
- a small number of repeatedly misclassified classes.

## Core paper

**Focal Loss for Dense Object Detection**  
Lin et al., ICCV 2017

Paper:  
https://openaccess.thecvf.com/content_iccv_2017/html/Lin_Focal_Loss_for_ICCV_2017_paper.html

A simple maintained PyTorch implementation:  
https://github.com/itakurah/focal-loss-pytorch

Modern detection frameworks also commonly include focal-loss variants.

## Possible experiment

```text
standard classification/objectness loss
              vs
          focal loss
```

Compare per-class recall, particularly on rare classes.

### Recommendation

Only use after checking the class distribution and per-class errors.

---

# 11. CutMix

## Why it could help

If baseline performance deteriorates when pills overlap or are partially occluded, augmentation may be a simpler solution than modifying the architecture.

## Core paper

**CutMix: Regularization Strategy to Train Strong Classifiers with Localizable Features**  
Yun et al., ICCV 2019

Paper:  
https://openaccess.thecvf.com/content_ICCV_2019/html/Yun_CutMix_Regularization_Strategy_to_Train_Strong_Classifiers_With_Localizable_Features_ICCV_2019_paper.html

Official PyTorch code:  
https://github.com/clovaai/CutMix-PyTorch

## Possible adaptation

For medication images, augmentation should be designed carefully so that bounding boxes and class labels remain valid.

Possible test:

```text
normal augmentation
        vs
occlusion-aware / CutMix-style augmentation
```

Evaluate specifically on overlapping and partially visible pills.

### Recommendation

Useful if robustness is a major weakness.

---

# 12. Mixup

## Core paper

**mixup: Beyond Empirical Risk Minimization**  
Zhang et al., ICLR 2018

Paper:  
https://openreview.net/forum?id=r1Ddp1-Rb

Paper implementation:  
https://github.com/facebookresearch/mixup-cifar10

Alternative author implementation:  
https://github.com/hongyi-zhang/mixup

## Potential role

Mixup can improve regularization and generalization, but it may be less naturally interpretable for pill detection than domain-specific augmentation.

### Recommendation

Lower priority than CutMix or real medication-specific augmentation.

---

# 13. The Most Important Baseline: Simple Prescription-Aware Constraint

Before implementing Deep Sets, Set Transformer, or GAT, first build a **simple non-neural prescription-aware baseline**.

Example:

```text
YOLO probabilities:
A = 0.42
B = 0.45
C = 0.08

Prescription candidates:
A, C, D

Vision only:
→ B

Prescription-constrained prediction:
→ A
```

Possible variants:

### Hard constraint

Remove classes not present in the prescription.

### Soft prior

```text
final_score(class)
    = visual_score(class)
      × prescription_prior(class)
```

### Top-k context reranking

Use the prescription only when the visual model is uncertain.

This simple baseline is critical because any advanced learned-context model must beat it.

No special paper is required to implement this baseline; it is an experimental control.

---

# 14. Recommended Research Sequence for This Capstone

## Stage 1 — Baseline

```text
VAIPE
 ↓
YOLO11
 ↓
Detection + counting
 ↓
Prescription matching
 ↓
FAR / FRR / mAP
```

Do not add new methodology yet.

---

## Stage 2 — Error Analysis

Create failure groups:

```text
A. visually similar pills
B. occlusion / overlap
C. class imbalance
D. confidence overestimation
E. context-related mistakes
F. low-quality / lighting cases
```

Measure how many errors belong to each category.

---

## Stage 3 — First Improvements

Recommended first two:

### Improvement 1

**Confidence calibration**

Why:

- extremely cheap
- directly connected to FAR
- strong safety interpretation

### Improvement 2

**Reject uncertain cases**

Why:

- realistic for medication verification
- avoids forcing dangerous decisions
- creates a useful risk–coverage experiment

---

## Stage 4 — Prescription-Aware Improvement

Start with:

```text
YOLO + simple prescription constraint
```

Then, only if there is evidence it is worthwhile:

```text
Deep Sets
   ↓
Set Transformer
   ↓
GAT (optional)
```

---

## Stage 5 — Fine-Grained Improvement

If visually similar pills dominate the errors:

```text
Supervised Contrastive Learning
            or
Deep Metric Learning
```

---

## Stage 6 — Robustness Improvement

If occlusion/background/lighting dominate:

```text
CutMix / targeted augmentation
```

If class imbalance dominates:

```text
Focal Loss / class-balanced sampling
```

---

# 15. Candidate Ablation Table

A final thesis experiment could eventually look like this:

| Method | mAP | Verification Accuracy | FAR | FRR | Coverage |
|---|---:|---:|---:|---:|---:|
| YOLO baseline | TBD | TBD | TBD | TBD | 100% |
| + confidence calibration | TBD | TBD | TBD | TBD | 100% |
| + reject option | TBD | TBD | TBD | TBD | TBD |
| + prescription constraint | TBD | TBD | TBD | TBD | TBD |
| + learned context | TBD | TBD | TBD | TBD | TBD |

This gives a much stronger research story than only reporting that a new model has slightly higher mAP.

---

# 16. Reading Priority

## Must read before proposing improvements

1. **On Calibration of Modern Neural Networks**
2. **SelectiveNet**
3. **Supervised Contrastive Learning**
4. **Deep Sets**

## Read if baseline indicates the corresponding problem

5. **PyTorch Metric Learning**
6. **Set Transformer**
7. **Focal Loss**
8. **CutMix**

## Advanced / optional

9. **Graph Attention Networks**
10. **Mixup**

---

# 17. Decision Rule

The project should follow this rule:

> **Every improvement must be justified by a measured baseline failure and evaluated against the simplest alternative.**

Examples:

- Do not add GAT unless context errors are demonstrated.
- Do not add focal loss unless class imbalance matters.
- Do not add contrastive learning unless similar-class confusion matters.
- Do not add augmentation unless robustness failures are demonstrated.

This prevents the project from becoming a collection of unrelated deep-learning techniques and keeps the final thesis scientifically defensible.
