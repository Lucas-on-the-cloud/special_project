# WGN results

AUC values below are percentages. Missing cells are pending, not zero. Synthetic smoke-test numbers and 5-epoch pilots are excluded.

| Model | FF++ c23 frame | FF++ c40 frame | FaceShifter c23 frame | FaceShifter c40 frame | Celeb-DF official video | DFDC video | WildDeepfake video |
|---|---:|---:|---:|---:|---:|---:|---:|
| WGN reproduced reference (EXP-002) | 98.21 | pending | pending | pending | 70.14 | 69.67 | 71.54 |
| gradient | 98.52 | pending | pending | pending | 68.31 | 69.87 | 72.17 |
| curriculum | 98.34 | pending | pending | pending | 63.71 | 67.75 | 69.85 |
| temporal sampling control | 98.27 | pending | pending | pending | 71.92 | 70.78 | 75.10 |
| temporal | 98.58 | 70.51 | 71.17 | 59.88 | 71.03 | 68.89 | 71.72 |
| degradation_control | 98.30 | 76.70 | 76.39 | 62.31 | 80.93 | 73.34 | 76.39 |
| degradation_consistency | 98.22 | 75.56 | 76.39 | 60.64 | 79.94 | 73.76 | 76.10 |

Celeb-DF v2 uses the authors' MP4 archive, the official 518-video test list, uniform 32-frame sampling, and the same WGN MTCNN crop code. The earlier DeepfakeBench measurements remain archived for provenance and are excluded from current comparisons.

## Candidate selection

A strict finalist must gain at least 2 pp on Celeb-DF, lose no more than 1 pp on FF++ c23, improve at least two generalization targets by 0.5 pp, and regress by no more than 2 pp on any generalization target. If none passes, a non-dominated method meeting the last three conditions is marked diagnostic eligible.

| Method | c23 loss | Celeb gain | Improved targets | Worst target regression | Pareto | Decision |
|---|---:|---:|---:|---:|---:|---|
| gradient | pending | pending | pending | pending | pending | pending |
| curriculum | pending | pending | pending | pending | pending | pending |
| temporal sampling control | pending | pending | pending | pending | pending | pending |
| temporal | pending | pending | pending | pending | pending | pending |
| degradation_control | pending | pending | pending | pending | pending | pending |
| degradation_consistency | pending | pending | pending | pending | pending | pending |

**Recommended cross-manipulation follow-up:** pending completion of the common sweep.

## Cross-manipulation follow-up

| Method/train group | Mean frame AUC including diagonal | Unseen mean frame AUC |
|---|---:|---:|
