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
- [ ] Finish ACPDS dataset download/preparation.
- [ ] Run pretrained evaluation and save actual metrics.
- [ ] Complete the short smoke-training run.
- [ ] Compare observed output with the paper/repository claim.

## Important correction to earlier assumptions

The ACPDS dataset contains only 293 source images, but the value of the paper is not simply the image count. It provides labeled parking-space polygons, an official code path, pretrained assets, and a split intended to avoid reusing the same views across partitions. It is appropriate as a **reproduction starting point**, not as the only evidence for a final thesis.

## Week 1 deliverables

1. `notebooks/acpds-paper-reproduction-kaggle.ipynb`
2. Updated project scope and README
3. Parking literature table
4. Dataset catalogue
5. Method-improvement shortlist

## Evidence still needed

Do not fill in accuracy, loss, runtime, or reproduction success until the notebook cells have actually produced those values. Save:

- Kaggle hardware and package versions;
- official Git commit;
- downloaded dataset file counts;
- pretrained evaluation metrics;
- smoke-training log;
- final confusion matrix and per-class metrics;
- deviations from the official instructions.

## Next action — one step at a time

Run the ACPDS notebook through the dataset-preparation cell. Verify the discovered dataset paths and class counts before starting pretrained evaluation. If that cell succeeds, record its output here and continue to only the next evaluation cell.

## Week 2 preview

- complete and document ACPDS reproduction;
- read ACPDS, PKLot, CNRPark+EXT, and the systematic review in detail;
- create a deterministic dataset manifest;
- decide the first modern backbone only after the official baseline is understood.

