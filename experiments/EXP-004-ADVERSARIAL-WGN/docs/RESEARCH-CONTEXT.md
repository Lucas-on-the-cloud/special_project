# Research context and experiment dependency

## Current scope clarification — 2026-11-15

EXP-004 applies Jia frequency-domain attacks to frozen reproduced WGN on FF++, DFDC, Celeb-DF-v2 official-direct and WildDeepfake. The user subsequently replaced the EXP-005 architecture draft with a separate Hou StatAttack/MStatAttack study. EXP-005 planning must not change EXP-004's locked algorithms, metrics or interpretation. Future architecture work depends on both attack studies; the old RCWG draft is archived.

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

### EXP-005 — A second attack study using Hou2023

Purpose: a separate study of StatAttack and MStatAttack on the same frozen checkpoint and four processed test cohorts. It needs real-reference feature distributions and an audited WGN adapter. Its implementation, live status and results are managed separately from this EXP-004 publication; it does not train a defense or activate the former RCWG prototype.

Future defense/architecture work remains unnumbered and conditional on evidence from the attacks and causal/ablation controls. It would require comparison with standard adversarial training, adaptive evaluation, clean/generalization retention and computational-cost analysis.

## Claim discipline

Permitted after EXP-004 only if supported by results:
- "Under threat model T and attack A, WGN's fake-to-real ASR is X."
- "Successful attacks are associated with Y change in WGSA diagnostics."

Not permitted without causal controls:
- "WGSA causes the adversarial vulnerability."
- "Frequency attacks always defeat WGN."
- "The model is adversarially robust" because one attack fails.

Not permitted as claims about the archived prototype:
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
       v
EXP-005 Hou statistical-consistency attack evaluation
       |
       v
Joint evidence review and causal/ablation controls
       |
       +-- no supported weakness --> revise research question
       |
       +-- supported weakness --> future defense design
                                      |
                                      v
                              adaptive evaluation and
                              contribution assessment
```
