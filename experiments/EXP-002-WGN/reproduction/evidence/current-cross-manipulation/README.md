# Current WGN cross-manipulation reproduction

Four independent WGN models were trained for 25 epochs on one FF++ c23 manipulation and evaluated on all four manipulation test sets. Values are frame-level AUC (%).

### Paper — Table 3

| Train / Test | DF | F2F | FS | NT | Avg |
|---|---:|---:|---:|---:|---:|
| DF | 99.93 | 72.94 | 39.02 | 77.73 | 72.40 |
| F2F | 84.31 | 99.23 | 52.19 | 70.13 | 76.47 |
| FS | 64.53 | 69.93 | 99.79 | 48.31 | 70.64 |
| NT | 88.51 | 70.56 | 46.74 | 97.93 | 75.93 |

### Historical RTX 5090 reproduction

| Train / Test | DF | F2F | FS | NT | Avg |
|---|---:|---:|---:|---:|---:|
| DF | 99.83 | 73.49 | 43.35 | 72.76 | 72.36 |
| F2F | 77.40 | 99.04 | 56.29 | 66.41 | 74.79 |
| FS | 55.76 | 69.99 | 99.80 | 49.68 | 68.80 |
| NT | 80.62 | 64.97 | 42.11 | 97.66 | 71.34 |

### Current RTX 5060 Ti reproduction

| Train / Test | DF | F2F | FS | NT | Avg |
|---|---:|---:|---:|---:|---:|
| DF | 99.79 | 61.84 | 44.84 | 70.60 | 69.27 |
| F2F | 72.71 | 99.08 | 67.18 | 67.04 | 76.50 |
| FS | 47.11 | 69.42 | 99.88 | 43.03 | 64.86 |
| NT | 84.61 | 71.06 | 44.59 | 97.89 | 74.54 |

## Overall comparison

| Source | All 16 cells | Unseen 12 cells (derived) |
|---|---:|---:|
| Paper | 73.86 | 65.41 |
| Historical RTX 5090 | 71.82 | 62.74 |
| Current RTX 5060 Ti | 71.29 | 62.00 |

The four current checkpoints and SHA-256 files are stored under `../../artifacts/current-cross-manipulation/`.
