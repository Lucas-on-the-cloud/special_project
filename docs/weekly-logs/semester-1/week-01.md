# Semester 1 — Week 01

**Period:** 2026-09-14 to 2026-09-20
**Stage:** Project foundation, literature orientation, and pipeline smoke test

## Weekly Goal

Build a reproducible project foundation and verify that a pretrained YOLO model
can run inference on sample UAV images. The goal is not to train a final model
or propose a new method this week.

## Success Criteria

- [ ] The local Python environment can be recreated.
- [ ] At least four core papers have been read or skimmed as planned.
- [ ] Several VisDrone sample images have been inspected.
- [ ] Pretrained YOLO inference runs successfully on at least one sample image.
- [ ] Prediction images and initial observations are saved.
- [ ] The next steps for `EXP-001` are clear.

## Task Checklist

### 1. Repository and environment

- [x] Create the GitHub repository.
- [x] Create the initial repository structure.
- [x] Add the project README.
- [ ] Create and activate a Python virtual environment.
- [ ] Install the initial dependencies.
- [ ] Record the Python, PyTorch, CUDA, and GPU versions.
- [ ] Confirm that Git ignores datasets, weights, virtual environments, and
      generated experiment outputs.

### 2. Literature review

- [ ] Read the VisDrone benchmark paper carefully.
- [ ] Read the main ideas of Feature Pyramid Networks (FPN).
- [ ] Read the multi-scale training section of YOLO9000.
- [ ] Skim SAHI and understand its slicing-and-merging pipeline.
- [ ] Update [`paper-table.md`](../../literature-review/paper-table.md) after
      reading each paper.

Questions to answer:

1. Why are objects in UAV images difficult to detect?
2. What information is lost when a high-resolution UAV image is resized?
3. How do feature pyramids and multi-scale training address scale variation?
4. Why can sliced inference improve small-object detection?
5. What computational cost does fixed tiling introduce?

### 3. Dataset exploration

- [ ] Download or select several VisDrone sample images.
- [ ] Inspect image resolutions, object sizes, class distribution, density, and
      occlusion.
- [ ] Do not commit the full dataset to GitHub.
- [ ] Record where the local dataset is stored.

### 4. Pretrained inference smoke test

- [ ] Run a pretrained Ultralytics YOLO model on the sample images.
- [ ] Save prediction images under `results/smoke-test/` locally.
- [ ] Record the model name, image size, confidence threshold, device, and
      inference time.
- [ ] Note obvious false positives, false negatives, and missed small objects.

## Work Completed

Record completed work here during the week.

- Repository initialized with a README and weekly-log structure.
- Tentative topic selected: *Improving Small Object Detection in UAV Imagery
  Using Adaptive Image Tiling and Multi-Scale Training*.

## Papers Read

| Paper | Reading level | Main takeaway | Status |
| ----- | ------------- | ------------- | ------ |
| VisDrone benchmark | Careful read | To be completed | Not started |
| FPN | Main concepts | To be completed | Not started |
| YOLO9000 | Multi-scale section | To be completed | Not started |
| SAHI | Initial skim | To be completed | Not started |

## Experiment / Smoke-Test Record

| Field | Value |
| ----- | ----- |
| Run ID | `SMOKE-001` |
| Model | TBD |
| Weights | TBD |
| Dataset/sample | TBD |
| Image size | TBD |
| Confidence threshold | TBD |
| Device | TBD |
| Output directory | `results/smoke-test/` |
| Result | Not run |

## Problems Encountered

- None recorded yet.

## What I Learned

- To be updated after reading and inference.

## Advisor Feedback

- No feedback recorded yet.

## Plan for Week 02

1. Prepare the VisDrone dataset for the selected YOLO framework.
2. Verify the annotations and train/validation split.
3. Define the configuration for `EXP-001`.
4. Train and evaluate the first YOLO baseline.
5. Record mAP@0.5, mAP@0.5:0.95, precision, recall, training time, and hardware.

## Weekly Summary

Complete this section at the end of the week in 5–8 sentences. State what was
completed, what was not completed, the main evidence produced, the largest
problem, and the highest-priority task for Week 02.
