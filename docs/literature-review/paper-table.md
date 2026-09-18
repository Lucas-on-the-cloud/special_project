# Literature Review: Parking Occupancy and Robustness

This table contains **17 parking-specific papers** plus **5 general improvement-method papers**. It is a research map, not a requirement to implement every paper.

## A. Parking-specific literature

| # | Paper (year) | Focus | Dataset/code | How it informs this project | Priority |
|---:|---|---|---|---|---|
| 1 | [Image-Based Parking Space Occupancy Classification: Dataset and Baseline](https://arxiv.org/abs/2107.12207) (2021, preprint) | Compact occupancy dataset and CNN baseline | [Official repository](https://github.com/martin-marek/parking-space-occupancy) | Reproduced in EXP-001: 97.99% pretrained and 97.72% independently trained test accuracy | **Reproduced** |
| 2 | [PKLot—A robust dataset for parking lot classification](https://doi.org/10.1016/j.eswa.2015.02.009) (2015) | Large multi-lot, multi-weather occupancy benchmark | [Official dataset](https://web.inf.ufpr.br/vri/databases/parking-lot-database/) | Main dataset and weather-aware evaluation | **Read now** |
| 3 | [Deep learning for decentralized parking lot occupancy detection](https://doi.org/10.1016/j.eswa.2016.10.055) (2017) | Decentralized CNN occupancy classification; CNRPark+EXT | [Paper/data record](https://openportal.isti.cnr.it/doc?id=people______::f0ae3d0d7a052b367753c8a217c77897) | External dataset and camera/weather domain shift | **Read now** |
| 4 | [Vision-based parking lot occupancy detection methods: A systematic review](https://arxiv.org/abs/2203.06463) (2022) | Datasets, methods, evaluation weaknesses, open problems | Review | Establish research gap and avoid misleading frame-level splits | **Read now** |
| 5 | [Real-time image-based parking occupancy detection using deep learning](https://ceur-ws.org/Vol-2087/paper5.pdf) (2018) | CNN features plus SVM; transfer evaluation | [Author code](https://github.com/debaditya-unimelb/real-time-car-parking-occupancy) | Early application-oriented transfer-learning baseline | Read next |
| 6 | [Transfer Learning for Classification of Parking Spots Using Residual Networks](https://doi.org/10.1016/j.trpro.2019.07.184) (2019) | Residual-network transfer learning | PKLot/parking crops | Supports a modern ResNet baseline and limited-data setting | Read next |
| 7 | [Parking Lot Occupancy Detection with Improved MobileNetV3](https://doi.org/10.3390/s23177642) (2023) | Lightweight classifier for deployment | Parking occupancy datasets | Backbone/efficiency comparison; consult the [published correction](https://www.mdpi.com/1424-8220/24/16/5236) | Read next |
| 8 | [Smart Parking Space Detection under Hazy Conditions](https://arxiv.org/abs/2201.05858) (2022, preprint) | Haze-aware parking occupancy | Parking images under degraded visibility | Condition-specific robustness and error categories | Read next |
| 9 | [Generalized parking occupancy analysis based on dilated CNN](https://doi.org/10.3390/s19020277) (2019) | Generalized occupancy classification with dilated convolutions | PKLot/CNRPark-style benchmarks | Compare claimed generalization with our cross-lot protocol | Later |
| 10 | [Car parking occupancy detection using smart camera networks and deep learning](https://doi.org/10.1109/ISCC.2016.7543901) (2016) | Smart-camera network and CNN application | CNRPark lineage | System architecture and edge-deployment context | Later |
| 11 | [A visual sensor network for parking lot occupancy detection in smart cities](https://doi.org/10.1109/WF-IoT.2015.7389147) (2015) | Distributed visual sensing for smart parking | Camera network | Application motivation and system constraints | Later |
| 12 | [Automated Parking Space Detection Using Convolutional Neural Networks](https://arxiv.org/abs/2106.07228) (2021, preprint) | Occupancy classification with saved parking polygons | Public implementation described in paper | Confirms the practical predefined-polygon pipeline | Later |
| 13 | [Automatic Vision-Based Parking Slot Detection and Occupancy Classification](https://arxiv.org/abs/2308.08192) (2023) | Automatic slot localization plus ResNet occupancy classification | PKLot, CNRPark+EXT | Future removal of predefined polygons; not Semester 1 core | Future work |
| 14 | [Vehicle Occurrence-Based Parking Space Detection](https://arxiv.org/abs/2306.09940) (2023) | Learns slot coordinates from repeated vehicle occurrences | Vehicle instance segmentation/heatmaps | Application extension using historical camera footage | Future work |
| 15 | [DMPR-PS: A Novel Approach for Parking-Slot Detection Using Directional Marking-Point Regression](https://github.com/Teoge/DMPR-PS) (2019) | Directional marking-point regression | Official code; ps2.0 | Strong reference for automatic slot geometry | Future work |
| 16 | [Vision-Based Parking-Slot Detection: A DCNN-Based Approach and a Large-Scale Benchmark Dataset](https://cslinzhang.github.io/deepps/) (2018) | DeepPS detector and Tongji ps2.0 benchmark | Project page and dataset | Benchmark for around-view slot detection under varied conditions | Future work |
| 17 | [Context-Based Parking Slot Detection With a Realistic Dataset](https://doi.org/10.1109/ACCESS.2020.3024668) (2020) | Context-aware slot detection and SNU dataset | [Official code/data](https://github.com/dohoseok/context-based-parking-slot-detect) | Realistic slot attributes/conditions for future extension | Future work |

Additional optional automatic-slot references:

- [End-to-End Trainable One-Stage Parking Slot Detection Integrating Global and Local Information](https://arxiv.org/abs/2003.02445)
- [Attentional Graph Neural Network for Parking-Slot Detection](https://arxiv.org/abs/2104.02576) and [official code](https://github.com/Jiaolong/gcn-parking-slot)
- [SUPS: A Simulated Underground Parking Scenario Dataset](https://arxiv.org/abs/2302.12966) and [data/code](https://github.com/jarvishou829/SUPS)
- [Parking Slot Detection on Around-View Images Using DCNN](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2020.00046/full)

## B. Five general method-improvement papers

| # | Paper (year) | Method type | Proposed use | Code | Priority |
|---:|---|---|---|---|---|
| M1 | [RandAugment: Practical Automated Data Augmentation with a Reduced Search Space](https://arxiv.org/abs/1909.13719) (2020) | Generic augmentation | Low-cost augmentation baseline | `torchvision.transforms.RandAugment` | **Implement** |
| M2 | [AugMix: A Simple Data Processing Method to Improve Robustness and Uncertainty](https://arxiv.org/abs/1912.02781) (2020) | Corruption robustness/consistency | Weather and image-corruption robustness | [Official code](https://github.com/google-research/augmix) | **Implement** |
| M3 | [Domain Generalization with MixStyle](https://arxiv.org/abs/2104.02008) (2021) | Feature-level domain generalization | Generalize across camera/background/weather styles | [Official code](https://github.com/KaiyangZhou/mixstyle-release) | Implement after baseline |
| M4 | [Deep CORAL: Correlation Alignment for Deep Domain Adaptation](https://arxiv.org/abs/1607.01719) (2016) | Unsupervised domain adaptation | Adapt with unlabeled target-lot images | Straightforward loss; community implementations | Optional |
| M5 | [Tent: Fully Test-Time Adaptation by Entropy Minimization](https://arxiv.org/abs/2006.10726) (2021) | Test-time adaptation | Adapt to target camera/weather batches at deployment | [Official code](https://github.com/DequanWang/tent) | Optional |

See [method-improvement.md](method-improvement.md) for assumptions and a fair experimental sequence.

## Reading order

### Week 1: establish the problem

1. ACPDS: read Abstract, Introduction, Dataset, Experimental Setup, Results, and repository README.
2. Systematic review: focus on datasets, evaluation practices, limitations, and future work.
3. PKLot: understand parking lots, weather categories, annotations, and official organization.
4. CNRPark+EXT: understand cameras, patches, conditions, and intended decentralized deployment.

### Week 2: establish modern application baselines

5. Real-time occupancy detection.
6. Residual-network transfer learning.
7. Improved MobileNetV3, including its correction.
8. Hazy-condition parking detection.

### After the domain gap is measured

9. RandAugment and AugMix.
10. MixStyle.
11. Deep CORAL or Tent only if deployment assumptions justify target-domain access.

Automatic slot-detection papers are for Related Work and future scope; they should not delay the occupancy baseline.

## Paper-review template

Create notes using this template:

```markdown
# Paper title

- Citation / link:
- Research problem:
- Dataset and split:
- Input and labels:
- Baseline:
- Proposed method:
- Metrics:
- Main result:
- Code/checkpoint available:
- Reproducibility concerns:
- Limitation or gap:
- How this affects our project:
- One experiment inspired by the paper:
```

## Evidence rules

- Distinguish peer-reviewed articles from preprints.
- Prefer official project pages, publisher/DOI pages, and author repositories.
- Verify reported dataset sizes against the downloaded files before using them in the thesis.
- Do not copy headline accuracy without also recording the split and whether test scenes were independent.
- A paper with code is easier to reproduce, but code availability does not guarantee a fair evaluation protocol.
