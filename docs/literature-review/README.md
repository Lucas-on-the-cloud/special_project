# Deepfake Literature Intake

The first source set has been received. Weeks 1–3 established the background on manipulation types, compression, generalization, spectral bias, and demographic fairness. Week 4 evaluates five 2026 sources assigned by the advisor.

## Source intake table

| ID | Source | Type | Code | Data/weights | Proposed role | Verification status |
|---|---|---|---|---|---|---|
| W1-01 | FaceForensics++ | Benchmark paper | Public framework/data by request | Dataset protocol | Manipulation taxonomy and compression background | Reviewed |
| W2-01 | UCF | Generalizable detector | Public research code to verify before use | Paper resources | Generalization background | Reviewed at report level |
| W2-02 | FreqDebias | Frequency-debiasing method | To verify | Paper resources | Spectral-bias background | Reviewed at report level |
| W2-03 | Synergistic Fairness Optimization | Fairness method | To verify | Paper resources | Demographic fairness background | Reviewed at report level |
| W4-01 | NTIRE 2026 complementary ensemble | Paper + repository | Yes | Pretrained weights | Robustness reference / inference fallback | Initial audit complete |
| W4-02 | DFD-HR | CVPR paper + repository | Yes | Checkpoint released | Preferred reproduction candidate | Initial audit complete |
| W4-03 | VRAG-DFD | CVPR Findings paper + repository link | Yes | Training resources require further audit | Interpretability and future work | Initial audit complete |
| W4-04 | Domain-incremental curriculum | CVPR Workshop paper | No official code link found in the paper | DF40 + recent-generator data | Continual-learning reference | Initial audit complete |
| W4-05 | WGN | CVPR Workshop paper | No official code link found in the paper | FF++, FaceShifter, Celeb-DF, DFDC, WDF | Candidate lightweight improvement | Initial audit complete |

See [`week-04-paper-matrix.md`](week-04-paper-matrix.md) for the detailed feasibility comparison.

## Review order

For every supplied source:

1. verify the official paper/project/repository;
2. identify the exact detection task and input unit;
3. record datasets, splits, manipulation types, and metrics;
4. check code, checkpoints, license, and Kaggle feasibility;
5. distinguish reported results from reproducible resources;
6. state how the source changes the project scope;
7. classify it as baseline, dataset, improvement, evaluation reference, or background only.

## Paper-note template

```markdown
# Paper title

- Citation / official link:
- Publication status and venue:
- Research problem:
- Input unit: image / frame / video / multimodal
- Manipulation types:
- Dataset and split:
- Baseline:
- Proposed method:
- Metrics:
- Main result:
- Official code:
- Pretrained weights:
- Reproduction instructions:
- Kaggle feasibility:
- Generalization evaluation:
- Limitations:
- How it affects our project:
- Candidate experiment:
```

## Code-first selection rule

Implementation priority:

```text
Official code + accessible public data + weights/instructions
                         ↓
Official code + accessible data
                         ↓
Public data + maintained framework implementation
                         ↓
Paper used for background only
```
