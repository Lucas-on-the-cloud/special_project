# Deepfake Literature Intake

The literature review is organized into two two-week reading blocks:

- **Weeks 1–2:** the five papers cited in the progress report.
- **Weeks 3–4:** the five newer sources assigned by the professor.

## Source intake table

| ID | Source | Type | Code | Data/weights | Proposed role | Verification status |
|---|---|---|---|---|---|---|
| W01–02-01 | Analyzing Fairness in Deepfake Detection With Massively Annotated Databases | Fairness analysis | To verify before implementation | Annotated benchmark resources | Demographic-bias background | Reviewed at report level |
| W01–02-02 | FaceForensics++ | Benchmark paper | Public framework/data by request | Dataset protocol | Manipulation taxonomy and compression background | Reviewed at report level |
| W01–02-03 | FreqDebias | Frequency-debiasing method | To verify before implementation | Paper resources | Spectral-bias and generalization background | Reviewed at report level |
| W01–02-04 | Synergistic Fairness Optimization for Deepfake Detection | Fairness method | To verify before implementation | Paper resources | Fairness-method background | Reviewed at report level |
| W01–02-05 | UCF: Unsupervised Cross-domain Deepfake Detection | Generalizable detector | To verify before implementation | Paper resources | Cross-domain background | Reviewed at report level |
| W03–04-01 | NTIRE 2026 complementary ensemble | Paper + repository | Yes | Pretrained weights | Robustness reference / inference fallback | Initial audit complete; reading continues |
| W03–04-02 | DFD-HR | CVPR paper + repository | Yes | Checkpoint released | Preferred reproduction candidate | Initial audit complete; reading continues |
| W03–04-03 | VRAG-DFD | CVPR Findings paper + repository link | Yes | Training resources require further audit | Interpretability and future work | Initial audit complete; reading continues |
| W03–04-04 | Domain-incremental curriculum | CVPR Workshop paper | No official code link found in the paper | DF40 + recent-generator data | Continual-learning reference | Initial audit complete; reading continues |
| W03–04-05 | WGN | CVPR Workshop paper | No official code link found in the paper | FF++, FaceShifter, Celeb-DF, DFDC, WDF | Candidate lightweight improvement | Detailed review complete; simplified reimplementation candidate |

See [`week-04-paper-matrix.md`](week-04-paper-matrix.md) for the detailed comparison of the **Weeks 3–4** paper set.

## Detailed paper notes

- [WGN: Wavelet-Guided Network for Efficient and Generalised Deepfake Detection](wgn-wavelet-guided-network.md) — detailed reading complete; simplified Kaggle reimplementation is feasible but no official code was located.

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
