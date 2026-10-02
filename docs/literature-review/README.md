# Deepfake Literature Intake

No paper or dataset has been approved yet. This file will be updated when the new materials are provided.

## Source intake table

| ID | Source | Type | Code | Data/weights | Proposed role | Verification status |
|---|---|---|---|---|---|---|
| — | Awaiting supplied materials | — | — | — | Scope formation | Pending |

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

