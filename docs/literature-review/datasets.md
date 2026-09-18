# Parking Dataset Catalogue

This catalogue separates datasets needed for the main occupancy-classification project from datasets useful only if automatic parking-slot localization becomes future work.

## Recommended dataset stack

| Priority | Dataset | Task and approximate size | Conditions/labels | Planned role | Official source |
|---:|---|---|---|---|---|
| 1 | ACPDS | 293 parking-lot images with space polygons and occupied/vacant labels | Unique viewpoints; official train/validation/test organization | Paper reproduction and pipeline smoke test | [Paper](https://arxiv.org/abs/2107.12207), [code/data](https://github.com/martin-marek/parking-space-occupancy) |
| 2 | PKLot | 12,417 full images and roughly 696k labeled parking-space crops | Three parking lots; sunny, cloudy, and rainy | Main training and leave-one-lot/weather benchmark | [Official dataset](https://web.inf.ufpr.br/vri/databases/parking-lot-database/), [paper](https://doi.org/10.1016/j.eswa.2015.02.009) |
| 3 | CNRPark+EXT | Roughly 150k labeled patches from 164 spaces | Multiple viewpoints, weather, and illumination | External test and optional target-domain adaptation | [Paper/data record](https://openportal.isti.cnr.it/doc?id=people______::f0ae3d0d7a052b367753c8a217c77897) |
| 4 | Tongji ps2.0 | 12,165 around-view images (9,827 train, 2,338 test) | Indoor/outdoor, rain, shadow, street light, slanted slots | Optional automatic slot-detection research | [DeepPS project and dataset](https://cslinzhang.github.io/deepps/) |
| 5 | SNU Context-Based Parking Slot Dataset | 22,817 images | Realistic external conditions and parking-slot attributes | Optional context-aware slot detection | [Code/data](https://github.com/dohoseok/context-based-parking-slot-detect), [paper](https://doi.org/10.1109/ACCESS.2020.3024668) |
| 6 | SUPS | Simulated underground parking, multi-sensor annotations | Low light, underground structure, synthetic variation | Optional synthetic pretraining/domain-shift study | [Paper](https://arxiv.org/abs/2302.12966), [code/data](https://github.com/jarvishou829/SUPS) |

Sizes are approximate catalogue values. Record the exact downloaded version and file counts before reporting experiments.

## Which datasets should actually be used?

### Semester 1

1. Start with **ACPDS** because its paper, repository, labels, pretrained model, and training scripts form a compact reproduction target.
2. Move to **PKLot** for the main experiments because parking-lot identity and weather categories support the research questions.
3. Add **CNRPark+EXT** only after the PKLot baseline is deterministic. Treat it as an untouched external test set at first.

This is enough for a strong project. Do not download all six datasets immediately.

### Future work only

Tongji ps2.0, SNU, and SUPS address parking-slot geometry/localization more directly. They become relevant only if predefined polygons are later removed from the application assumptions.

## Evaluation protocols

### Protocol A — Official ACPDS reproduction

- Use the repository's stated split and model configuration.
- Record the official Git commit and any changes required for current Kaggle packages.
- Compare pretrained evaluation with a short smoke-training run before a full run.

### Protocol B — PKLot leave-one-parking-lot-out

For each fold:

- train on two parking lots;
- validate using held-out sequences from the training lots;
- test once on the unseen third lot;
- report per-lot and aggregate metrics.

Do not randomly shuffle image crops across the entire dataset.

### Protocol C — Weather holdout

- Train on selected weather categories.
- Test on a held-out weather category when the dataset distribution is sufficient.
- Keep parking-lot and temporal leakage under control; weather alone is not a valid split if near-identical frames cross partitions.

### Protocol D — Cross-dataset

- Train and select hyperparameters on PKLot only.
- Map labels to a shared binary occupied/vacant definition.
- Evaluate the frozen model on CNRPark+EXT.
- If adaptation is studied, separate the zero-shot result from results that used unlabeled target images.

## Leakage checklist

Before training, answer all of the following:

- Are neighboring frames from one video sequence present in different splits?
- Does one physical parking space appear in both train and test under almost identical conditions?
- Is the test parking lot unseen during training?
- Were target-test labels used to tune thresholds or augmentation?
- Are multiple crops from the same source frame grouped together?

If the answer to the first, second, or fifth question is “yes,” revise the split.

## Storage and repository policy

- Datasets live in Kaggle inputs or `/kaggle/working`, never in Git.
- Commit manifests, download instructions, split CSVs, and small metric files only.
- Record dataset URL, license/terms, download date, archive checksum, extracted file count, and exclusions.
- Do not redistribute a dataset unless its license explicitly allows it.

## Dataset manifest template

```yaml
name: PKLot
source_url: https://web.inf.ufpr.br/vri/databases/parking-lot-database/
downloaded_at: YYYY-MM-DD
archive_sha256: ...
full_images: ...
space_crops: ...
parking_lots: ...
split_protocol: leave-one-parking-lot-out
excluded_files: []
notes: ...
```

