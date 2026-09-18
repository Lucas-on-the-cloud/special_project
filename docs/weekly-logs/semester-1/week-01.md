# Semester 1 — Week 01

## Week goal

Select an application-oriented computer-vision problem, define a feasible research question, and make the first official baseline runnable on Kaggle.

## Topic exploration

The project initially explored UAV small-object detection and then medication verification. Both directions were kept as learning history, but they are no longer the active scope.

The current direction is:

> **Robust Vision-Based Parking Occupancy Monitoring Across Different Parking Lots and Weather Conditions**

Why this direction was selected:

- it has a clear real-world application;
- public datasets and baseline code exist;
- the binary occupied/vacant task is feasible for a first research project;
- generalization across cameras, parking lots, weather, and lighting creates a measurable research question;
- an end-to-end visual demo can be built without hardware.

## Scope decision

The first system uses predefined parking-space polygons and classifies each crop as occupied or vacant. Automatic slot localization, tracking, license plates, payments, and IoT integration are outside the initial scope.

## Reproduction selected

**Paper:** Image-Based Parking Space Occupancy Classification: Dataset and Baseline

**Official repository:** `martin-marek/parking-space-occupancy`

**Observed official revision during the Kaggle clone:**

```text
17da2c8b33055be8019483260f0efbcbdfda0478
```

The repository cloned successfully and exposed the expected `dataset`, `models`, `notebooks`, `utils`, and training files.

## Kaggle environment

The project will run on Kaggle rather than the local Windows Python installation. A GPU-compatible Kaggle runtime is required. Earlier environment checks showed that accelerator type and the installed PyTorch CUDA architectures must be compatible; change the Kaggle accelerator/runtime if a P100 compatibility warning appears.

## Work completed

- [x] Pivoted the active topic to parking occupancy monitoring.
- [x] Defined the application boundary and research questions.
- [x] Chosen ACPDS as the first reproducibility target.
- [x] Cloned and inspected the official ACPDS repository on Kaggle.
- [x] Created a complete Kaggle reproduction notebook.
- [x] Catalogued 17 parking papers and 5 method-improvement papers.
- [x] Catalogued 6 datasets and selected 3 for the main project.
- [x] Finished ACPDS dataset download/preparation.
- [x] Evaluated the official pretrained model: **97.99% test accuracy**.
- [x] Completed the five-epoch smoke run: **96.44% test accuracy**.
- [x] Completed one 100-epoch `RCNN-128-square` run: **97.72% test accuracy**.
- [x] Compared the result with the paper's `97.97 ± 0.07%` result for the same setting.

## Important correction to earlier assumptions

The ACPDS dataset contains only 293 source images, but the value of the paper is not simply the image count. It provides labeled parking-space polygons, an official code path, pretrained assets, and a split intended to avoid reusing the same views across partitions. It is appropriate as a **reproduction starting point**, not as the only evidence for a final thesis.

## Week 1 deliverables

1. `notebooks/acpds-paper-reproduction-kaggle.ipynb`
2. Updated project scope and README
3. Parking literature table
4. Dataset catalogue
5. Method-improvement shortlist

## EXP-001 result

| Run | Epochs | Test loss | Test accuracy |
|---|---:|---:|---:|
| Official pretrained model | — | 0.1695 | **97.99%** |
| Smoke training | 5 | 0.0934 | 96.44% |
| Independent full training | 100 | 0.1711 | **97.72%** |
| Paper, same configuration | 100 | — | **97.97 ± 0.07%** |

Environment: Python 3.12.13, PyTorch 2.10.0+cu128, Torchvision 0.25.0+cu128, Tesla T4, seed 42. Official repository commit: `17da2c8b33055be8019483260f0efbcbdfda0478`.

The pretrained checkpoint almost exactly reproduces the paper result. The independently trained model is 0.25 percentage points below the reported mean. This is treated as a successful close reproduction, not an exact statistical replication, because only one seed was trained and the software environment differs from the original 2021 setup.

The full run reached 100% training accuracy and 98.84% final validation accuracy. Validation loss was lowest at epoch 24 and increased later while validation accuracy remained high, so future experiments should preserve both the final checkpoint and the checkpoint with the best validation criterion.

Compact logs, hashes, and learning curves are recorded in `experiments/EXP-001-acpds-reproduction/` and `results/EXP-001-acpds-reproduction/`. Model checkpoints and the 168 MB export archive are excluded from Git.

## Next action — one step at a time

Start Week 2 by reading the ACPDS method/evaluation sections against the observed results, then define the first modern lightweight baseline. Do not begin robustness improvements until the dataset split and evaluation protocol are fixed.

## Week 2 preview

- use the completed ACPDS reproduction as the reference baseline;
- read ACPDS, PKLot, CNRPark+EXT, and the systematic review in detail;
- create a deterministic dataset manifest;
- decide the first modern backbone only after the official baseline is understood.
