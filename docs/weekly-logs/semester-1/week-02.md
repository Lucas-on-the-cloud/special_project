# Semester 1 — Week 02 — Complete

**Status:** Completed  
**Outcome:** EXP-001 was converted from a successful code run into a documented and understood paper reproduction.

## Week goal

Convert the completed ACPDS reproduction into research understanding, then prepare a leakage-resistant PKLot experiment.

## Completed

- [x] Read the ACPDS Abstract, Dataset, Models, Training Details, Results, and Model Comparison sections.
- [x] Explained why 293 full images produce 11,236 parking-space examples.
- [x] Understood parking-lot-separated train/validation/test splits and unseen-lot generalization.
- [x] Explained the R-CNN input, ROI pooling, and occupied/vacant output.
- [x] Compared square and quadrilateral pooling.
- [x] Explained the 100-epoch learning-rate schedule and backbone freezing.
- [x] Explained why the paper performs 12 settings × 5 runs.
- [x] Compared the best R-CNN and Faster R-CNN FPN settings.
- [x] Documented the accuracy–deployment trade-off.

Detailed notes: [`../../literature-review/acpds-paper-notes.md`](../../literature-review/acpds-paper-notes.md)

## Key understanding

The most important lesson is that high occupancy accuracy is only meaningful when the evaluation prevents the same physical scene or near-duplicate frames from leaking into both training and test data. Model selection must use validation data; the test set should estimate final generalization.

## Current evidence

- Official pretrained ACPDS test accuracy: 97.99%.
- Independent 100-epoch ACPDS test accuracy: 97.72%.
- Paper mean for the same configuration: 97.97 ± 0.07%.

## Week 03 handoff

Create EXP-002 as a **PKLot dataset audit and split-validation notebook** on Kaggle. Before training any model, it must report dataset structure, parking lots, weather categories, class balance, temporal/file grouping, duplicates or near-duplicates, and proposed train/validation/test partitions.

No robustness method will be implemented until this split is verified.
