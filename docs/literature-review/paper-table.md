# Literature Review Tracker

This table tracks the papers most relevant to the tentative topic:
*Improving Small Object Detection in UAV Imagery Using Adaptive Image Tiling
and Multi-Scale Training*.

## Reading Priority

| Priority | Paper | Year | Role in this project | Reading plan | Status |
| -------- | ----- | ---- | -------------------- | ------------ | ------ |
| 1 | [Vision Meets Drones: A Challenge](https://arxiv.org/abs/1804.07437) | 2018 | VisDrone benchmark and problem definition | Careful read | Not started |
| 2 | [Feature Pyramid Networks for Object Detection](https://openaccess.thecvf.com/content_cvpr_2017/html/Lin_Feature_Pyramid_Networks_CVPR_2017_paper.html) | 2017 | Multi-scale feature foundation | Main concepts | Not started |
| 3 | [YOLO9000: Better, Faster, Stronger](https://openaccess.thecvf.com/content_cvpr_2017/html/Redmon_YOLO9000_Better_Faster_CVPR_2017_paper.html) | 2017 | Multi-scale training foundation | Relevant sections | Not started |
| 4 | [An Analysis of Scale Invariance in Object Detection (SNIP)](https://openaccess.thecvf.com/content_cvpr_2018/html/Singh_An_Analysis_of_CVPR_2018_paper.html) | 2018 | Scale-normalized training | Careful read | Not started |
| 5 | [SNIPER: Efficient Multi-Scale Training](https://arxiv.org/abs/1805.09300) | 2018 | Efficient chip-based multi-scale training | Careful read | Not started |
| 6 | [Slicing Aided Hyper Inference and Fine-Tuning (SAHI)](https://arxiv.org/abs/2202.06934) | 2022 | Fixed-slicing baseline | Very careful read + reproduce | Not started |
| 7 | [Adaptive Slicing-Aided Hyper Inference (ASAHI)](https://www.mdpi.com/2072-4292/15/5/1249) | 2023 | Key adaptive-slicing related work | Very careful read | Not started |
| 8 | [Clustered Object Detection in Aerial Images (ClusDet)](https://openaccess.thecvf.com/content_ICCV_2019/html/Yang_Clustered_Object_Detection_in_Aerial_Images_ICCV_2019_paper.html) | 2019 | Object-cluster-aware cropping | Main concepts | Not started |
| 9 | [Drone-YOLO](https://ieeexplore.ieee.org/document/10270571/) | 2023 | UAV-specific YOLO improvements | Main concepts | Not started |

## Detailed Review Table

Fill one row after reading each paper. Use your own words and record exact table,
figure, or section numbers for results that may later be cited in the report.

| Paper | Problem | Main method | Dataset | Metrics / key result | Code | Limitation | Useful for our project? |
| ----- | ------- | ----------- | ------- | -------------------- | ---- | ---------- | ----------------------- |
| VisDrone | TBD | Benchmark | VisDrone | TBD | TBD | TBD | Dataset and problem definition |
| FPN | TBD | Feature pyramid | COCO | TBD | TBD | TBD | Theoretical background |
| YOLO9000 | TBD | Multi-scale training | TBD | TBD | TBD | TBD | Training strategy |
| SNIP | TBD | Scale normalization | COCO | TBD | TBD | TBD | Scale-aware training idea |
| SNIPER | TBD | Object-focused chips | COCO | TBD | TBD | TBD | Efficient crop selection idea |
| SAHI | TBD | Sliced training/inference | VisDrone, xView | TBD | Yes | TBD | Fixed-tiling baseline |
| ASAHI | TBD | Adaptive slicing | TBD | TBD | TBD | TBD | Closest related method |
| ClusDet | TBD | Cluster-region detection | VisDrone, UAVDT, DOTA | TBD | TBD | TBD | Region-selection idea |
| Drone-YOLO | TBD | UAV-specific YOLO modifications | VisDrone | TBD | TBD | TBD | UAV detector comparison |

## Reading Notes Template

For each paper, create a separate note only when the paper is important enough
to require more detail. Use this structure:

```text
Citation:
Research problem:
Main idea:
Method/pipeline:
Dataset and experimental setup:
Key results:
Limitations:
What can be reproduced:
How it relates to this project:
Questions:
```
