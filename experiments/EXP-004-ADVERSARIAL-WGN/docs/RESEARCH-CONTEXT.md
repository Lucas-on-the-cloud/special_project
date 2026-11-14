# Research context and experiment dependency

## Project storyline

This repository follows a staged research program rather than independent code demos.

### EXP-002 — Reproduce WGN
Purpose: reconstruct the WGN architecture and reproduce the paper-aligned training/evaluation pipeline.

Frozen reference:
- MobileViT-S backbone
- WGSA with Haar DWT / adaptive subband gates / IDWT attention
- FF++ c23 training
- 256x256 MTCNN face crops
- frozen reference checkpoint SHA256:
  `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6`
- reproduced FF++ c23 test: frame ACC 93.92%, frame AUC 98.21%

EXP-002 is the scientific control. EXP-004 must not modify it.

### EXP-003 — Generalization improvement exploration
Purpose: evaluate architecture/training changes for cross-dataset/generalization. Gradient, curriculum, temporal and degradation candidates are separate from the adversarial-resilience branch. Their results provide project context but are not the victim models for the primary EXP-004 protocol.

### EXP-004 — Challenge WGN using adversarial attacks from prior literature
Purpose: answer whether the frozen WGN can be fooled by adversarial mechanisms developed in the adversarial/deepfake literature.

Core logic:

```
Reproduced WGN (EXP-002)
        |
        v
Prior-paper attack mechanism
(Jia 2022 frequency adversarial attack;
standard FGSM/PGD baselines)
        |
        v
Adversarial fake face x_adv
        |
        v
Frozen WGN inference
        |
        +--> Fake remains Fake: attack failed
        |
        +--> Fake becomes Real: successful evasion
        |
        v
WGSA mechanism diagnostics
(subband statistics, gates, attention)
```

EXP-004 is **evaluation**, not model improvement. It must preserve model weights, dataset splits and threshold.

### EXP-005 — Develop a defense module only after EXP-004
Purpose: if EXP-004 establishes a reproducible adversarial vulnerability, identify the failure mechanism and design a new defense module integrated into WGSA/WGN.

The intended publication contribution is not simply "WGN + one extra module." A defensible contribution requires:
1. a verified vulnerability/failure mechanism;
2. a method motivated by that mechanism;
3. comparison with existing defenses and standard adversarial training;
4. adaptive attacks against the defended model;
5. preservation or improvement of clean and cross-domain generalization;
6. ablation and computational-cost analysis.

If EXP-004 does not establish a meaningful vulnerability, EXP-005 must revise the hypothesis rather than fabricate a defense problem.

## Claim discipline

Permitted after EXP-004 only if supported by results:
- "Under threat model T and attack A, WGN's fake-to-real ASR is X."
- "Successful attacks are associated with Y change in WGSA diagnostics."

Not permitted without causal controls:
- "WGSA causes the adversarial vulnerability."
- "Frequency attacks always defeat WGN."
- "The model is adversarially robust" because one attack fails.

Not permitted for EXP-005 until validated:
- "RCWG is a novel defense."
- "RCWG improves generalization/robustness."

## Dependency gate

```
EXP-002 reproduced baseline
       |
       v
EXP-004 clean-reference validation
       |
       v
EXP-004 paper-grounded attacks + mechanism measurements
       |
       +-- no meaningful vulnerability --> revise research question
       |
       +-- meaningful vulnerability
               |
               v
       causal/ablation analysis
               |
               v
       EXP-005 defense module
               |
               v
       adaptive defense evaluation + generalization
               |
               v
       paper contribution assessment
```
