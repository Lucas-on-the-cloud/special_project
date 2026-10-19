# WGN results

AUC values below are percentages. Missing cells are pending, not zero. Synthetic smoke-test numbers and 5-epoch pilots are excluded.

| Model | FF++ c23 frame | FF++ c40 frame | FaceShifter c23 frame | FaceShifter c40 frame | Celeb-DF official video | DFDC video | WildDeepfake video |
|---|---:|---:|---:|---:|---:|---:|---:|
| WGN reproduced reference (EXP-002) | 98.21 | 72.22 | 72.37 | 63.43 | 70.14 | 69.67 | 71.54 |
| gradient | 98.52 | 70.60 | 74.39 | 62.73 | 68.31 | 69.87 | 72.17 |
| curriculum | 98.34 | 71.34 | 72.30 | 60.96 | 63.71 | 67.75 | 69.85 |
| temporal sampling control | 98.27 | 70.27 | 71.40 | 59.98 | 71.92 | 70.78 | 75.10 |
| temporal | 98.58 | 70.51 | 71.17 | 59.88 | 71.03 | 68.89 | 71.72 |
| degradation_control | 98.30 | 76.70 | 76.39 | 62.31 | 80.93 | 73.34 | 76.39 |
| degradation_consistency | 98.22 | 75.56 | 76.39 | 60.64 | 79.94 | 73.76 | 76.10 |

Celeb-DF v2 uses the authors' MP4 archive, the official 518-video test list, uniform 32-frame sampling, and the same WGN MTCNN crop code. The earlier DeepfakeBench measurements remain archived for provenance and are excluded from current comparisons.

## Candidate selection

A strict finalist must gain at least 2 pp on Celeb-DF, lose no more than 1 pp on FF++ c23, improve at least two generalization targets by 0.5 pp, and regress by no more than 2 pp on any generalization target. If none passes, a non-dominated method meeting the last three conditions is marked diagnostic eligible.

| Method | c23 loss | Celeb gain | Improved targets | Worst target regression | Pareto | Decision |
|---|---:|---:|---:|---:|---:|---|
| gradient | -0.30 | -1.83 | 2/6 | 1.83 | yes | diagnostic eligible |
| curriculum | -0.13 | -6.43 | 0/6 | 6.43 | no | not retained |
| temporal sampling control | -0.06 | +1.78 | 3/6 | 3.45 | no | not retained |
| temporal | -0.37 | +0.89 | 1/6 | 3.55 | no | not retained |
| degradation_control | -0.09 | +10.79 | 5/6 | 1.12 | yes | strict finalist |
| degradation_consistency | -0.00 | +9.80 | 5/6 | 2.79 | yes | not retained |

**Recommended cross-manipulation follow-up:** degradation_control.

## Cross-manipulation follow-up

| Method/train group | Mean frame AUC including diagonal | Unseen mean frame AUC |
|---|---:|---:|
