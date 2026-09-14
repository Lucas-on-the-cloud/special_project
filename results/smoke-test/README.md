# SMOKE-001 — Pretrained YOLO on VisDrone

This directory contains the outputs of the Week 01 pipeline smoke test.

## Purpose

The run verifies that the Kaggle environment, VisDrone image loading,
Ultralytics YOLO inference, visualization, and result-export pipeline work end
to end.

This is **not** a VisDrone baseline evaluation. The model uses COCO-pretrained
weights and the eight images are only a qualitative sample. The reported
detections and timing must not be presented as VisDrone mAP results.

## Configuration

| Field | Value |
| ----- | ----- |
| Run ID | `SMOKE-001` |
| Model | YOLO11n |
| Weights | `yolo11n.pt` (COCO pretrained) |
| Images | 8 VisDrone2019-DET validation images |
| Image size | 640 |
| Confidence threshold | 0.25 |
| IoU threshold | 0.70 |
| Device | Tesla T4, GPU 0 |

See `run_metadata.json` for software versions and
`smoke_test_summary.csv` for per-image detections and reported speed.

## Initial Observations

- Medium and large vehicles were detected more consistently than tiny objects.
- Distant pedestrians, motorcycles, bicycles, and vehicles were often missed.
- Some class mismatches appeared, including `traffic light` and `potted plant`.
- One overexposed image produced only one detection despite containing many
  visible road objects.
- Fixed and adaptive tiling remain hypotheses to test after establishing a
  VisDrone-trained baseline.
