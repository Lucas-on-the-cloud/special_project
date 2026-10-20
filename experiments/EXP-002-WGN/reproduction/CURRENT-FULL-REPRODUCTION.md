# Current RTX 5060 Ti WGN reproduction

This report follows the three evaluation tables used by the archived RTX 5090 reproduction.

## Table 1 — independently trained in-domain models

| Experiment | Paper ACC | Paper AUC | RTX 5090 ACC | RTX 5090 AUC | RTX 5060 Ti ACC | RTX 5060 Ti AUC | Δ AUC vs paper |
|---|---:|---:|---:|---:|---:|---:|---:|
| FF++ c23 | 95.32 | 98.90 | 94.12 | 98.44 | 93.92 | 98.21 | -0.69 pp |
| FF++ c40 | 80.20 | 89.00 | 78.80 | 87.09 | 78.93 | 87.80 | -1.20 pp |
| FaceShifter c23 | 98.00 | 99.92 | 98.24 | 98.88 | 98.37 | 99.10 | -0.82 pp |
| FaceShifter c40 | 94.99 | 98.66 | 93.87 | 97.20 | 94.07 | 97.22 | -1.44 pp |

## Table 2 — cross-dataset from the FF++ c23 checkpoint

| Target | Paper AUC | RTX 5090 frame/video AUC | RTX 5060 Ti frame/video AUC |
|---|---:|---:|---:|
| Celeb-DF v2 | 77.62 | 65.03 / 69.70 | 63.58 / 67.44 |
| DFDC | 70.41 | 69.54 / 71.00 | 69.08 / 69.67 |
| WildDeepfake | 68.65 | 70.35 / 75.35 | 70.92 / 71.54 |

For strict comparison with RTX 5090, the Celeb-DF row uses the same 16,420-frame manifest. The separately preserved official-direct pipeline has 16,576 frames and 70.14% video AUC.

## Table 3 — cross-manipulation

### Paper

| Train / Test | DF | F2F | FS | NT | Avg |
|---|---:|---:|---:|---:|---:|
| DF | 99.93 | 72.94 | 39.02 | 77.73 | 72.40 |
| F2F | 84.31 | 99.23 | 52.19 | 70.13 | 76.47 |
| FS | 64.53 | 69.93 | 99.79 | 48.31 | 70.64 |
| NT | 88.51 | 70.56 | 46.74 | 97.93 | 75.93 |

### Historical RTX 5090

| Train / Test | DF | F2F | FS | NT | Avg |
|---|---:|---:|---:|---:|---:|
| DF | 99.83 | 73.49 | 43.35 | 72.76 | 72.36 |
| F2F | 77.40 | 99.04 | 56.29 | 66.41 | 74.79 |
| FS | 55.76 | 69.99 | 99.80 | 49.68 | 68.80 |
| NT | 80.62 | 64.97 | 42.11 | 97.66 | 71.34 |

### Current RTX 5060 Ti

| Train / Test | DF | F2F | FS | NT | Avg |
|---|---:|---:|---:|---:|---:|
| DF | 99.79 | 61.84 | 44.84 | 70.60 | 69.27 |
| F2F | 72.71 | 99.08 | 67.18 | 67.04 | 76.50 |
| FS | 47.11 | 69.42 | 99.88 | 43.03 | 64.86 |
| NT | 84.61 | 71.06 | 44.59 | 97.89 | 74.54 |

## Table 3 overall

| Source | All 16 cells | Unseen 12 cells |
|---|---:|---:|
| Paper | 73.86 | 65.41 |
| Historical RTX 5090 | 71.82 | 62.74 |
| Current RTX 5060 Ti | 71.29 | 62.00 |
