# WGN — Discussion Notes

**Paper:** [WGN: Wavelet-Guided Network for Efficient and Generalised Deepfake Detection](https://openaccess.thecvf.com/content/CVPR2026W/PPMisDet/html/Ghosh_WGN_Wavelet-Guided_Network_for_Efficient_and_Generalised_Deepfake_Detection_CVPRW_2026_paper.html)  
**Authors:** Tanusree Ghosh and Ruchira Naskar  
**Reading completed:** 2026-10-04

This note contains only the concepts, interpretations, and conclusions developed during our step-by-step discussion.

## 1. Problem we understood

Spatial-domain detectors learn features from image locations, textures, edges, facial components, and other RGB information. However, they can overfit to semantic content such as identity, hairstyle, background, lighting, or expressions instead of learning universal forgery traces.

This becomes a problem in real deployment because deepfakes may be produced by different generation pipelines and repeatedly post-processed through resizing, compression, or enhancement.

Our conclusion:

> A detector can perform very well inside its training dataset while failing on unseen datasets or manipulation methods because it learned dataset-specific or semantic shortcuts.

## 2. Why frequency information is useful

Manipulation artifacts can include:

- unnatural smoothing or skin micro-texture;
- blending boundaries;
- warping discontinuities;
- resampling traces;
- ringing or checkerboard patterns;
- generator-specific noise.

These artifacts may be weak and localized in RGB space. Frequency analysis can make some of them easier to detect.

Wavelets are useful because they provide both frequency information and approximate information about where the response occurs. WGN therefore uses frequency information to **guide spatial feature learning** instead of building a large independent frequency stream and a heavy fusion module.

## 3. Pipeline we discussed

~~~mermaid
flowchart TD
    A["Input face image"] --> B["MobileViT-S backbone: feature F"]
    B --> C["Channel pooling: mean + max"]
    C --> D["Haar DWT: LL, LH, HL, HH"]
    D --> E["Adaptive subband gating"]
    E --> F["Weighted subbands + IDWT"]
    F --> G["Spatial attention map A"]
    B --> H["F_att = F × A"]
    G --> H
    B --> I["Keep original feature F"]
    H --> J["Concatenate F and F_att"]
    I --> J
    J --> K["1×1 convolution"]
    K --> L["Global average pooling"]
    L --> M["Linear classifier: real or fake"]
~~~

## 4. What each pipeline step means

### 4.1 Backbone feature \(F\)

MobileViT-S converts the input face into multiple feature maps:

\[
F \in \mathbb{R}^{C \times H \times W}.
\]

- \(C\) is the number of feature channels.
- \(H \times W\) preserves approximate spatial position.
- Different channels may respond to texture, boundaries, shapes, or other learned patterns.

Deepfake artifacts are often weak and local. If global pooling is applied directly to \(F\), these small responses can be diluted by the rest of the face or background.

### 4.2 Channel pooling

WGN combines mean pooling and max pooling across channels while retaining \(H \times W\).

Our interpretation:

- **Mean pooling** captures the overall activation at each position.
- **Max pooling** preserves a sparse but strong response from one or a few channels.
- Combining them gives a more stable guide without losing strong localized evidence.

The result is the single-channel guide map \(F_g\).

### 4.3 Haar DWT

Haar DWT decomposes \(F_g\) into:

| Subband | What we understood |
|---|---|
| LL | Coarse and low-frequency structure |
| LH | Directional detail |
| HL | Detail in the other direction |
| HH | Diagonal and high-frequency detail |

We concluded that WGN must retain LL because deepfake evidence may exist across multiple frequency ranges, not only in HH.

The Haar filters are fixed, so they add no learned filter parameters. The operation remains differentiable, allowing gradients to pass through it during training.

### 4.4 Adaptive subband gating

Different deepfake and post-processing methods may emphasize different frequency subbands. Therefore, WGN should not always assume that HH is the most important.

The model:

1. calculates the spatial mean of each subband;
2. forms a four-value frequency signature;
3. uses a small MLP to predict one weight for each subband;
4. emphasizes useful subbands and reduces less useful ones.

Our conclusion:

> Adaptive gating is necessary because different input images and manipulation pipelines leave different frequency signatures.

### 4.5 IDWT and attention map

Adaptive gating answers:

> Which frequency bands are important for this image?

IDWT converts the weighted subbands back to the spatial domain. It does not independently choose important positions; it reconstructs the weighted frequency responses into a map that preserves their locations.

The resulting attention map \(A\) answers:

> Where are the frequency-guided responses located?

Min-max normalization constrains the map to approximately \(0\)–\(1\).

### 4.6 Attention-modulated feature

WGN computes:

\[
F_{\text{att}} = F \times A.
\]

Example discussed:

- \(F = 0.8\)
- \(A = 0.9\)
- \(F_{\text{att}} = 0.72\)

The region is mostly preserved because the attention value is high. A low attention value suppresses the corresponding spatial position.

Therefore, \(F_{\text{att}}\) is not a completely new feature. It is a frequency-guided copy of \(F\).

### 4.7 Why retain both \(F\) and \(F_{\text{att}}\)

WGN concatenates:

- \(F\): complete original feature information;
- \(F_{\text{att}}\): feature information focused on suspicious regions.

If attention is imperfect, using only \(F_{\text{att}}\) may discard useful information. Retaining \(F\) provides a safety path.

If each tensor contains 128 channels:

\[
128 + 128 = 256 \text{ channels after concatenation}.
\]

### 4.8 Why use a \(1 \times 1\) convolution

A \(1 \times 1\) convolution mixes information across channels at each spatial position.

Example discussed:

\[
256 \times 16 \times 16
\rightarrow
128 \times 16 \times 16.
\]

It changes the number of channels but retains the \(16 \times 16\) spatial size when stride is one. Its purpose is to learn how to combine the original and attention-guided features with relatively low overhead.

### 4.9 Global pooling and classification

After fusion, global average pooling converts each channel into one value.

Example discussed:

\[
128 \times 16 \times 16
\rightarrow
\text{a vector containing 128 values}.
\]

A linear layer then produces a real/fake logit.

Global pooling is reasonable here because WGSA has already suppressed less relevant regions. This differs from pooling the unfiltered backbone feature directly.

## 5. How much mathematics we need

For our current goal, we do not need to derive or memorize every equation.

For each equation, we only need to identify:

1. the input;
2. the operation;
3. the output;
4. the purpose;
5. the tensor-shape change;
6. whether the operation is fixed or learnable.

A deeper mathematical derivation is only necessary if we later modify the transform or propose a new method.

## 6. Results we discussed

### 6.1 In-dataset and compression results

| Setting | Backbone ACC/AUC | WGN ACC/AUC | Our interpretation |
|---|---:|---:|---|
| FF++ C23 | 93.70 / 98.12 | **95.32 / 98.90** | WGN improves an already strong backbone |
| FF++ C40 | 79.90 / 88.68 | **80.20 / 89.00** | Best ACC, but not best AUC in the complete table |
| FaceShifter C40 | 93.30 / 97.28 | **94.99 / 98.66** | Strong and convincing improvement |

Our conclusion:

> WGN performs strongly, but it does not win every metric and should not be described as universally best.

### 6.2 Cross-dataset evaluation

The model is trained on FF++ C23 and tested directly on other datasets.

| Test dataset | WGN AUC | Our interpretation |
|---|---:|---|
| Celeb-DF | **77.62** | Strong; best in the table |
| DFDC | 70.41 | Competitive |
| WildDeepfake | 68.65 | Moderate and weaker than several methods |

Our conclusion:

> WGN has strong but dataset-dependent generalization. Its result on WildDeepfake is above random but should not automatically be called deployment-ready or acceptable for every application.

### 6.3 Cross-manipulation evaluation

WGN obtains the best reported average in three of four training settings, but the average includes the very high score on the manipulation seen during training.

Important unseen-manipulation results discussed:

- train DF, test FS: 39.02 AUC;
- train NT, test FS: 46.74 AUC;
- train FS, test NT: 48.31 AUC.

For train DF and test FS, 39.02 is higher than the compared methods, but it remains below random in absolute terms.

Our conclusion:

> WGN produces relative improvement in some difficult settings, but it does not solve cross-manipulation generalization.

## 7. Efficiency conclusion

WGN uses:

- 5.7M parameters;
- 3.7G FLOPs.

It has the fewest parameters in the reported comparison, but several models have fewer FLOPs.

Our conclusion:

> WGN is parameter-efficient, but it is not computationally cheapest. The paper also does not report enough latency or FPS evidence to claim that it is the fastest model.

## 8. Ablation conclusions

The most important comparison is:

| Variant | Average AUC |
|---|---:|
| Full WGN | **66.73** |
| Generic spatial attention without DWT | 64.71 |

Both variants have the same parameters and FLOPs. This supports the conclusion that improvement comes from wavelet-structured guidance, not simply from adding any attention module.

Other conclusions we discussed:

- Backbone only reaches 64.96; full WGN reaches 66.73.
- Fixed subband weights are worse, supporting adaptive gating.
- Mean-only pooling is worse than mean plus max.
- Removing LL is slightly worse, so useful evidence is not limited to high frequencies.
- HH alone is insufficient; multiple directional bands are useful.
- Addition or multiplication-only fusion is worse than concatenating \(F\) and \(F_{\text{att}}\).

## 9. Limitations we identified

- Cross-dataset performance decreases on WildDeepfake.
- Several cross-manipulation scores are near or below random.
- The model has the lowest parameter count but not the lowest FLOPs.
- It processes images/frames and does not model temporal consistency across video frames.
- Frequency-domain adversarial robustness is not evaluated.
- No official WGN code or checkpoint was located during our review.

## 10. Reproduction decision

A full reproduction is not the best first experiment because it requires:

- implementing WGSA from the paper;
- FaceForensics++ access and consistent face preprocessing;
- multiple manipulation subsets;
- several external test datasets;
- many training and evaluation runs.

A simplified Kaggle experiment remains feasible:

1. implement MobileViT-S backbone only;
2. implement MobileViT-S plus WGSA;
3. use the same split and training setup for both;
4. begin with the 10-epoch ablation protocol;
5. compare AUC, parameters, FLOPs, runtime, and GPU memory;
6. reproduce the **direction of improvement**, not necessarily every published number.

Final decision:

> Keep WGN as a method reference and simplified reimplementation candidate. Compare it with code-released papers before selecting the first reproduction target.
