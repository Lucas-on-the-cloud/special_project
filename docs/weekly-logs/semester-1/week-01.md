# Semester 1 — Week 01

**Period:** 2026-09-14 to 2026-09-20
**Stage:** Project foundation, literature orientation, and pipeline smoke test

## Weekly Goal

Build a reproducible project foundation and verify that a pretrained YOLO model
can run inference on sample UAV images. The goal is not to train a final model
or propose a new method this week.

## Success Criteria

- [x] The Kaggle Python environment can be recreated from the notebook.
- [ ] At least four core papers have been read or skimmed as planned.
- [x] Several VisDrone sample images have been inspected.
- [x] Pretrained YOLO inference runs successfully on sample images.
- [x] Prediction images and initial observations are saved.
- [x] The next steps for `EXP-001` are clear.

## Task Checklist

### 1. Repository and environment

- [x] Create the GitHub repository.
- [x] Create the initial repository structure.
- [x] Add the project README.
- [x] Configure a Kaggle notebook with a compatible GPU accelerator.
- [x] Install the initial dependencies in Kaggle.
- [x] Record the Python, PyTorch, CUDA, and GPU versions.
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

- [x] Download the VisDrone2019-DET validation split using the notebook.
- [x] Inspect image resolutions, object sizes, class distribution, density, and
      occlusion.
- [x] Do not commit the full dataset to GitHub.
- [x] Record the Kaggle dataset path: `/kaggle/working/datasets/VisDrone`.

### 4. Pretrained inference smoke test

- [x] Run a pretrained Ultralytics YOLO model on eight sample images.
- [x] Save prediction images under `results/smoke-test/`.
- [x] Record the model name, image size, confidence threshold, device, and
      inference time.
- [x] Note obvious false positives, false negatives, and missed small objects.

## Work Completed

Record completed work here during the week.

- Repository initialized with a README and weekly-log structure.
- Tentative topic selected: *Improving Small Object Detection in UAV Imagery
  Using Adaptive Image Tiling and Multi-Scale Training*.
- Created a reproducible Kaggle notebook for `SMOKE-001`.
- Configured two Tesla T4 GPUs and used GPU 0 for inference.
- Downloaded the VisDrone2019-DET validation split automatically.
- Ran COCO-pretrained YOLO11n inference on eight VisDrone validation images.
- Exported eight prediction images, a CSV summary, and run metadata.

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
| Model | Ultralytics YOLO11n |
| Weights | `yolo11n.pt` (COCO pretrained) |
| Dataset/sample | 8 VisDrone2019-DET validation images |
| Image size | 640 |
| Confidence threshold | 0.25 |
| IoU threshold | 0.70 |
| Device | Tesla T4, GPU 0 |
| Software | Python 3.12.13, PyTorch 2.10.0+cu128, Ultralytics 8.4.152 |
| Total detections | 89 across 8 images |
| Reported inference time | 5.207 ms/image (Ultralytics batch-level report) |
| Output directory | `results/smoke-test/` |
| Result | Completed |

## Problems Encountered

- Kaggle initially assigned a Tesla P100, whose `sm_60` compute capability was
  incompatible with the installed PyTorch CUDA 12.8 build. Switching the
  accelerator to Tesla T4 resolved the warning.
- `/kaggle/input` was initially empty. The notebook was updated to download the
  VisDrone validation split automatically when no attached input is found.

## What I Learned

- Medium and large vehicles were detected more consistently than distant small
  objects.
- Distant pedestrians, motorcycles, bicycles, and vehicles were frequently
  missed after resizing images to 640 pixels.
- False positives and class mismatches included `traffic light` and
  `potted plant`.
- An overexposed image produced only one detection despite containing many
  visible objects.
- These observations motivate a tiling experiment, but they do not prove that
  tiling is effective because the smoke-test model has not been trained on
  VisDrone.

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
