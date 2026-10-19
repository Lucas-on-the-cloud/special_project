# WGN results

AUC values below are percentages. Missing cells are pending, not zero. Synthetic smoke-test numbers and 5-epoch pilots are excluded.

| Model | FF++ c23 frame AUC | FF++ c40 frame AUC | Celeb-DF v2 official-direct video AUC | DFDC video AUC | WildDeepfake video AUC |
|---|---|---|---|---|---|
| WGN reproduced reference (EXP-002) | 98.21 | pending | 70.14 | 69.67 | 71.54 |
| gradient | 98.52 | pending | 68.31 | 69.87 | 72.17 |
| curriculum | 98.34 | pending | 63.71 | 67.75 | 69.85 |
| temporal_control | 98.27 | pending | 71.92 | 70.78 | 75.10 |
| temporal | 98.58 | 70.51 | 71.03 | 68.89 | 71.72 |
| degradation_control | pending | pending | pending | pending | pending |
| degradation_consistency | pending | pending | pending | pending | pending |

Celeb-DF v2 uses the authors' MP4 archive, the official 518-video test list, uniform 32-frame sampling, and the same WGN MTCNN crop code. The earlier DeepfakeBench measurements remain archived for provenance and are excluded from current comparisons.


Selection check: Celeb-DF video AUC gain >=2 percentage points; FF++ c23 frame AUC loss <=1 percentage point, relative to the EXP-002 reproduced WGN reference.

- gradient: Celeb-DF gain -1.83 pp; c23 loss -0.30 pp; does not meet initial criterion.
- curriculum: Celeb-DF gain -6.43 pp; c23 loss -0.13 pp; does not meet initial criterion.
- temporal: Celeb-DF gain +0.89 pp; c23 loss -0.37 pp; does not meet initial criterion.

## Cross-manipulation follow-up

| Method/train group | Mean frame AUC including diagonal | Unseen mean frame AUC |
|---|---|---|
