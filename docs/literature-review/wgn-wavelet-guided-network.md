# WGN: Wavelet-Guided Network for Efficient and Generalised Deepfake Detection

**Reading completed:** 2026-10-04  
**Authors:** Tanusree Ghosh and Ruchira Naskar  
**Venue:** CVPR 2026 Workshop on Perception and Persuasion in Misinformation Detection (PPMisDet)  
**Official paper:** https://openaccess.thecvf.com/content/CVPR2026W/PPMisDet/html/Ghosh_WGN_Wavelet-Guided_Network_for_Efficient_and_Generalised_Deepfake_Detection_CVPRW_2026_paper.html  
**Input unit:** Cropped face image/frame  
**Task:** Binary real/fake classification  
**Review status:** Detailed review complete  
**Code status checked on 2026-10-04:** No official implementation or pretrained checkpoint was located in the paper or author-linked search.

## 1. Research problem

Spatial-domain deepfake detectors can achieve high accuracy when training and testing data come from the same distribution. However, they can overfit to semantic content, identities, backgrounds, dataset statistics, or generator-specific RGB textures. Their performance can therefore decline on unseen manipulation methods, new datasets, and heavily compressed media.

Real-world deepfakes may come from diverse generation pipelines and may be resized, compressed, or enhanced multiple times. The paper asks whether explicit frequency-domain evidence can guide spatial feature learning without requiring a heavy multi-stream or transformer-based fusion system.

## 2. Main contribution

The paper proposes the **Wavelet-Guided Neural Network (WGN)**. Its main component is **Wavelet-Guided Spatial Attention (WGSA)**, a lightweight and backbone-agnostic attention module.

WGSA:

1. creates a single-channel spatial guide from backbone features;
2. applies a fixed, differentiable, single-level Haar DWT;
3. adaptively weights the LL, LH, HL, and HH frequency subbands;
4. reconstructs a spatial attention map with IDWT;
5. uses this map to suppress uninformative regions in the backbone feature map;
6. fuses the original and attention-modulated features for real/fake classification.

The primary backbone used in the paper is MobileViT-S.

## 3. Concepts needed to understand the paper

### Spatial features and semantic shortcuts

A spatial feature records **what pattern is present and where it occurs**. Examples include edges, skin texture, face boundaries, eye or mouth structure, and local blending traces.

Semantic content is the meaningful visible content of an image, such as identity, hairstyle, background, lighting, or expression. A detector may obtain good in-dataset results by learning correlations between these semantic properties and labels rather than learning universal forensic traces. This produces poor cross-dataset or cross-manipulation generalization.

### Why frequency guidance may help

Manipulation pipelines can introduce:

- unnatural smoothing or micro-texture;
- blending and warping discontinuities;
- resampling traces;
- ringing or checkerboard patterns;
- generator-specific noise.

These signals may be subtle in RGB space but clearer in frequency subbands. Wavelets are useful because they preserve both frequency information and approximate spatial location.

## 4. Methodology walkthrough

### 4.1 Backbone feature extraction

For an RGB input image \(x\) resized to \(256 \times 256\), MobileViT-S produces:

\[
F = \mathrm{Backbone}(x) \in \mathbb{R}^{C \times H \times W}.
\]

The channels act like stacked feature maps, while \(H \times W\) preserves approximate spatial location. Direct global pooling at this point may dilute artifacts because deepfake traces are often weak and localized.

### 4.2 Channel pooling

WGSA pools across the channel dimension while preserving \(H \times W\):

\[
F_g(i,j) = \frac{1}{2}
\left(
\mathrm{mean}_{c} F(c,i,j)
+
\mathrm{max}_{c} F(c,i,j)
\right).
\]

The mean term captures overall activation. The max term preserves sparse but strong responses that may occur in only a few channels. The result is a single-channel spatial guide:

\[
F_g \in \mathbb{R}^{1 \times H \times W}.
\]

### 4.3 Single-level Haar DWT

A fixed Haar DWT decomposes \(F_g\) into four subbands:

- **LL:** coarse or low-frequency structure;
- **LH and HL:** directional details;
- **HH:** diagonal and high-frequency details.

Each subband has spatial size \(H/2 \times W/2\). The Haar kernels are fixed, so this step adds no learned filter parameters, but convolution-based implementation allows gradients to pass through it.

The method keeps LL because manipulation evidence may occur across multiple frequency ranges, not only in the highest-frequency HH band.

### 4.4 Subband statistics and adaptive gating

WGSA takes the spatial mean of each subband:

\[
s = [\mu(LL), \mu(LH), \mu(HL), \mu(HH)].
\]

This four-value frequency signature is passed through a small MLP and sigmoid to produce sample-specific gates:

\[
w = [w_{LL}, w_{LH}, w_{HL}, w_{HH}], \quad w_k \in (0,1).
\]

Each band is reweighted:

\[
LL' = w_{LL}LL,\quad
LH' = w_{LH}LH,\quad
HL' = w_{HL}HL,\quad
HH' = w_{HH}HH.
\]

Adaptive gating is needed because different manipulation and post-processing pipelines do not produce their strongest evidence in the same frequency band.

### 4.5 IDWT and attention map

IDWT reconstructs the weighted subbands into a raw spatial attention map:

\[
[LL', LH', HL', HH'] \xrightarrow{\mathrm{IDWT}} A_{\mathrm{raw}}.
\]

Adaptive gating determines **which frequency bands are informative**. IDWT maps their weighted responses back to spatial coordinates, showing **where frequency-guided evidence occurs**.

Min-max normalization constrains the final attention map \(A\) to approximately \([0,1]\).

### 4.6 Feature modulation and fusion

The attention map is applied to every channel of the original feature map:

\[
F_{\mathrm{att}}(c,i,j) = F(c,i,j) A(i,j).
\]

Values of \(A\) near one preserve a spatial region; values near zero suppress it. The method retains both feature representations:

- \(F\): complete backbone information;
- \(F_{\mathrm{att}}\): a copy focused by wavelet-guided attention.

They are concatenated along the channel dimension. If each contains \(C\) channels, the concatenated tensor contains \(2C\) channels. A \(1 \times 1\) convolution mixes the original and attended channels and returns a fused tensor \(Z\) with \(C\) channels while preserving \(H \times W\).

Retaining both representations prevents an imperfect attention map from discarding all original semantic information.

### 4.7 Classification

Global average pooling converts \(Z \in \mathbb{R}^{C \times H \times W}\) into a vector of \(C\) values. A linear layer produces one binary real/fake logit. Global pooling is applied only after attention and fusion have suppressed irrelevant regions, rather than directly pooling the raw backbone feature.

## 5. Experiment setup

Main experiments:

- Framework: PyTorch
- Hardware: NVIDIA RTX A2000 12 GB
- Input resolution: \(256 \times 256\)
- Face detector/cropper: MTCNN
- Optimizer: Adam
- Initial learning rate: \(1 \times 10^{-4}\)
- Schedule: cosine annealing
- Loss: binary cross-entropy
- Batch size: 32
- Training budget: 25 epochs

The component ablation in Table 6 uses a different controlled setup: AdamW and 10 epochs.

FaceForensics++ contains 1,000 real and 4,000 manipulated videos across Deepfakes (DF), Face2Face (F2F), FaceSwap (FS), and NeuralTextures (NT). The official split is 720/140/140 train/validation/test videos. The main experiment samples ten frames per fake clip and forty frames per real clip. Since each real source has four manipulated versions, this keeps the real and fake frame totals approximately balanced.

Metrics:

- **ACC:** classification accuracy at a selected threshold;
- **AUC/AUROC:** ranking quality across thresholds and the main generalization metric.

## 6. Main results and interpretation

### 6.1 In-dataset and compressed evaluation

| Setting | Backbone ACC/AUC | WGN ACC/AUC | Critical interpretation |
|---|---:|---:|---|
| FF++ C23 | 93.70 / 98.12 | **95.32 / 98.90** | WGN improves an already strong baseline |
| FF++ C40 | 79.90 / 88.68 | **80.20 / 89.00** | Best ACC, but not the best AUC in the full comparison |
| FaceShifter C23 | 98.04 / 99.22 | 98.00 / **99.92** | Tied best AUC, not best ACC |
| FaceShifter C40 | 93.30 / 97.28 | **94.99 / 98.66** | Strongest WGN result in this table |

WGN does not win every metric. The correct conclusion is that it achieves strong and competitive in-domain/compressed performance rather than universal dominance.

### 6.2 Cross-dataset evaluation

Models are trained on FF++ C23 and tested directly on unseen datasets.

| Test dataset | WGN AUC | Best result in table | Interpretation |
|---|---:|---:|---|
| Celeb-DF | **77.62** | **77.62 WGN** | Strong generalization |
| DFDC | 70.41 | 71.28 MFFLE | Competitive |
| WildDeepfake | 68.65 | 74.51 DDAFM | Moderate and clearly weaker |

The evidence supports **strong but dataset-dependent** cross-dataset generalization. WildDeepfake remains a weakness; an AUC of 68.65 is above random but should not automatically be considered deployment-ready.

### 6.3 Cross-manipulation evaluation

WGN obtains the best reported average for models trained on DF, FS, and NT, but not when trained on F2F.

| Training manipulation | WGN average AUC | Best in comparison? |
|---|---:|---|
| DF | 72.40 | Yes |
| F2F | 76.47 | No; DDAFM reaches 79.31 |
| FS | 70.64 | Yes |
| NT | 75.93 | Yes, by a small margin |

The average includes the high in-domain diagonal result, so off-diagonal cells must also be inspected. Examples of weak unseen-manipulation transfer include:

- train DF, test FS: 39.02 AUC;
- train NT, test FS: 46.74 AUC;
- train FS, test NT: 48.31 AUC.

For train DF/test FS, 39.02 is better than the compared methods in that column, but it remains below random in absolute terms. Therefore WGN improves some difficult failure cases without solving general cross-manipulation detection.

## 7. Model efficiency

| Model | Parameters | FLOPs |
|---|---:|---:|
| WGN | **5.7 M** | 3.7 G |
| Xception | 22.1 M | 4.6 G |
| M2TR | 38.0 M | 4.6 G |
| EfficientNet-B4 | 17.5 M | **1.6 G** |
| MFFLE | 17.6 M | 2.0 G |

WGN is **parameter-efficient** because it has the fewest parameters in the comparison. It is not the computationally cheapest model because several alternatives use fewer FLOPs. The paper does not provide an FPS or latency comparison, so it does not establish that WGN is the fastest model in deployment.

## 8. Ablation study

The controlled Table 6 experiment trains on Real vs DF and evaluates DF, F2F, FS, and NT.

| Variant | Average AUC | What it tests |
|---|---:|---|
| Backbone only | 64.96 | Baseline |
| **Full WGN** | **66.73** | Proposed configuration |
| Generic spatial attention, no DWT | 64.71 | Frequency structure vs generic attention |
| Fixed band weights, no gating | 64.16 | Need for sample-adaptive gating |
| Mean-only guide pooling | 65.51 | Mean plus max vs mean alone |
| Sigmoid attention normalization | 65.76 | Min-max vs sigmoid |
| High-frequency only, no LL | 66.23 | Contribution of LL |
| HH only | 64.88 | Need for multiple directional bands |
| Addition fusion | 65.49 | Fusion strategy |
| Multiplication-only fusion | 65.22 | Need to retain original \(F\) |

Full WGN improves the backbone average by 1.77 AUC while adding 0.82 M parameters and 0.10 G FLOPs. Its largest gain is on unseen FaceSwap: 33.58 versus 28.78 AUC, although the absolute performance remains low.

The comparison between full WGN (66.73) and generic spatial attention without DWT (64.71) is particularly important: the variants have the same parameter and FLOP counts, so the result supports the value of wavelet-structured guidance rather than merely adding an attention block.

## 9. Strengths

- Clear and lightweight frequency-guided attention design.
- Fixed Haar filters add no learned filter parameters.
- Sample-adaptive frequency gating.
- The module retains spatial localization through DWT/IDWT.
- Strong parameter efficiency.
- Ablation covers nearly every important design decision.
- Simplified reimplementation is plausible on one Kaggle GPU.

## 10. Limitations

- Generalization is inconsistent across datasets, especially WildDeepfake.
- Some unseen-manipulation results remain close to or below random.
- Parameter count is lowest, but FLOPs are not.
- Evaluation is frame/image based and does not model temporal consistency in videos.
- No reported evaluation against frequency-domain adversarial attacks.
- No official code or pretrained checkpoint was located during this review.
- Full reproduction requires controlled face extraction, frame sampling, FF++ access, multiple manipulation subsets, and several external test datasets.

The authors identify temporal frequency-guided attention and resilience to adversarial frequency attacks as future work.

## 11. Reproducibility assessment

**Full paper reproduction:** Medium-high difficulty and not recommended as the first weekly reproduction.

Reasons:

- missing official code/checkpoint;
- dataset access and preprocessing burden;
- many in-domain, cross-dataset, and cross-manipulation runs;
- exact pipeline details must be reimplemented.

**Recommended Kaggle experiment:** simplified component reproduction.

1. Prepare a small, documented FF++ subset.
2. Use MobileViT-S with \(256 \times 256\) cropped faces.
3. Implement two controlled variants:
   - C0: backbone only;
   - C1: backbone plus WGSA.
4. Train each variant using the same seed, split, augmentation, and budget.
5. Begin with the 10-epoch ablation protocol.
6. Evaluate AUC on the seen DF manipulation and at least one unseen manipulation if accessible.
7. Report parameters, FLOPs, runtime, peak GPU memory, and AUC.
8. Treat success as reproducing the **direction of improvement**, not necessarily the exact published number.

## 12. Final assessment for the project

WGN is a strong **method reference** and a plausible **later improvement module** for the capstone. Its contribution is understandable, parameter-efficient, and supported by controlled ablation. However, the lack of official code and the data pipeline make it less suitable than a code-released paper for the first reproduction milestone.

**Decision:** retain WGN as a simplified reimplementation candidate; compare it with DFD-HR and the NTIRE codebase before selecting the week's reproduction target.
