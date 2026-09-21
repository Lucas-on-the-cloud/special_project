# ACPDS Paper Notes

## Citation

Martin Marek, *Image-Based Parking Space Occupancy Classification: Dataset and Baseline*, arXiv:2107.12207, 2021.

- Paper: https://arxiv.org/abs/2107.12207
- Official repository: https://github.com/martin-marek/parking-space-occupancy
- Reproduced in: [`EXP-001`](../../experiments/EXP-001-acpds-reproduction/README.md)

## 1. Research problem

The paper studies image-based classification of individual parking spaces as **occupied** or **vacant**. It assumes that the coordinates of every parking space are already known. The model does not automatically discover parking-space geometry.

The main concern is generalization: a model should recognize occupancy in a parking lot that was not present during training, rather than memorizing a familiar camera, background, or physical space.

## 2. Dataset

ACPDS, the Action-Camera Parking Dataset, contains:

| Split | Full images |
|---|---:|
| Train | 231 |
| Validation | 35 |
| Test | 27 |
| **Total** | **293** |

Although 293 full images appears small, each image contains many annotated parking spaces. Every annotated parking-space region is a separate occupied/vacant example. The full dataset contains **11,236 unique parking-space views**, including 5,376 occupied spaces.

Images were collected across tens of parking lots and streets under varied weather, lighting, viewpoint, and occupancy conditions. Each parking space is annotated with a quadrilateral aligned with its visible edges.

## 3. Why split by parking lot?

A random crop- or frame-level split can place the same physical parking space, camera background, or near-duplicate scene in both training and test data. A model may then memorize scene-specific features and produce an overestimated test score.

ACPDS assigns different physical parking lots to the train, validation, and test sets. Therefore, an **unseen parking lot** is a location whose layout, background, parking spaces, and viewpoint did not appear during training. The model already knows the occupied/vacant classes, but it must apply that knowledge to a new environment.

This split is central to our capstone because it separates genuine generalization from scene memorization.

## 4. Model input and output

The complete model receives:

1. one full parking-lot image; and
2. the quadrilateral coordinates of all known parking spaces in that image.

It returns two class logits—vacant and occupied—for every parking space. Applying softmax converts the logits into occupancy probabilities.

```text
Full image + N parking-space quadrilaterals
                    ↓
               ROI pooling
                    ↓
          N parking-space patches
                    ↓
        Occupied/vacant classification
```

## 5. R-CNN-inspired baseline

The R-CNN-inspired model crops each parking-space region directly from the high-resolution image and passes every crop independently through an ImageNet-pretrained ResNet50 binary classifier.

For `RCNN-128-square`:

- `RCNN` identifies the R-CNN-inspired per-region classifier;
- `128` means each pooled crop is resized to 128 × 128 pixels;
- `square` specifies the pooling method.

Because the patches are processed independently, there is no information flow between parking spaces after pooling. The pixels included in each crop determine how much context the classifier can use.

## 6. Pooling methods

### Quadrilateral pooling

Pixels inside the annotated parking-space quadrilateral are warped into a square patch. This focuses on the annotated space but contains little surrounding context and may distort strongly angled regions.

### Square pooling

A minimum bounding square around the quadrilateral is extracted and resized. The patch includes surrounding road, vehicles, and neighboring-space context.

Square context is especially useful for R-CNN when a car is occluded, extends beyond the marked space, or is difficult to recognize using only pixels inside the quadrilateral. The paper found square pooling consistently better than quadrilateral pooling in the tested configurations.

## 7. Faster R-CNN FPN-inspired baseline

The second architecture first processes a resized full image with a ResNet50 feature pyramid. It then pools features for each known parking-space region and classifies them.

Unlike the per-patch R-CNN model, its shared full-image backbone allows contextual information to flow between regions. However, it requires processing the entire image at a selected input resolution, which increases memory and compute cost at high resolution.

## 8. Training setup

- Optimizer: AdamW
- Total training: 100 epochs
- Epochs 1–50: learning rate `1e-4`
- Epochs 51–100: learning rate `1e-5`
- Mini-batch size: 1
- Augmentation: horizontal flip, rotation, brightness, contrast, saturation, and hue changes
- Pretrained backbone: ImageNet for R-CNN and COCO for Faster R-CNN FPN

The authors freeze Batch Normalization parameters/statistics and early backbone layers. This reduces overfitting on a relatively small dataset and avoids unstable BatchNorm updates with batch size one. Early pretrained layers already encode reusable low-level features such as edges, textures, and simple shapes.

## 9. Why 60 training runs?

The paper tests twelve configurations:

- R-CNN: 3 pooling resolutions × 2 pooling types = 6 settings;
- Faster R-CNN FPN: 3 full-image resolutions × 2 pooling types = 6 settings.

Each setting is trained five times with random initialization:

```text
12 settings × 5 runs = 60 training runs
```

The five runs are used to report mean accuracy and estimated standard error. The authors do not select the luckiest individual run. Model configuration is selected using validation accuracy so that the test set remains an unbiased estimate of generalization.

## 10. Main results

| Architecture | Pooling | Resolution | Validation accuracy | Test accuracy |
|---|---|---:|---:|---:|
| R-CNN | Square | 128 | **98.38 ± 0.06%** | **97.97 ± 0.07%** |
| Faster R-CNN FPN | Square | 1440 | **98.58 ± 0.07%** | **98.51 ± 0.10%** |

`RCNN-128-square` has the highest validation accuracy among R-CNN settings. `Faster R-CNN FPN-1440-square` has the highest validation accuracy in the complete comparison.

## 11. Accuracy versus deployment

Faster R-CNN FPN is more accurate in the reported experiment, but the authors consider R-CNN attractive for practical deployment:

- the full input image does not need to be resized to one fixed resolution;
- high- and low-resolution cameras can be supported as long as each parking-space crop contains enough pixels;
- compute grows with the number of parking spaces rather than always processing an expensive full-image backbone;
- it is suitable for CPU deployment and flexible camera configurations.

For a small number of spaces, per-patch R-CNN can be efficient. For many spaces, the shared-backbone FPN model may amortize its fixed full-image cost more effectively. Therefore, “best” depends on accuracy, camera resolution, number of spaces, latency, and hardware.

## 12. Failure cases and limitations

The paper identifies difficult cases involving:

- heavy vehicle-to-vehicle occlusion;
- large vehicles occupying multiple spaces;
- parking spaces occluded by trees;
- absence of snow conditions in the dataset;
- dependence on manually known parking-space coordinates.

ACPDS is also small at the full-image level and uses one camera family. High accuracy on ACPDS does not prove robustness to another dataset, camera system, or annotation format.

## 13. Our reproduction

| Run | Test accuracy |
|---|---:|
| Official pretrained checkpoint | **97.99%** |
| Five-epoch smoke run | 96.44% |
| Independent 100-epoch run, seed 42 | **97.72%** |
| Paper, `RCNN-128-square`, five-run mean | **97.97 ± 0.07%** |

The official checkpoint nearly exactly matches the paper. Our independent run is 0.25 percentage points below the reported mean. This is a successful close reproduction, not an exact statistical replication, because only one independent seed was trained and the current software environment differs from the 2021 environment.

## 14. Implications for our project

ACPDS establishes that a leakage-resistant parking-lot split is possible and that known-space classification can work on unseen locations. It does not answer whether the method transfers between public datasets or remains reliable under stronger weather/camera shifts.

Our next experiment will therefore audit PKLot and construct a leakage-resistant split before training a modern lightweight baseline. Robustness methods will be introduced only after the baseline domain gap is measured.

