# Week 4 Paper and Code Matrix

**Review date:** 2026-10-02  
**Reading period:** Weeks 3–4  
**Purpose:** compare the five newly assigned sources, decide what to read deeply, what to reproduce on Kaggle, and what to defer.

## Comparison

| Source | Core idea | Reported evaluation/resources | Code status | Kaggle assessment | Project role |
|---|---|---|---|---|---|
| [NTIRE 2026 repository](https://github.com/khoalephanminh/ntire26-deepfake-challenge) / [paper](https://arxiv.org/abs/2604.25889) | Extreme compound degradation plus three complementary DINOv2/CLIP streams and calibrated voting to reduce spatial attention drift | Fourth place in the NTIRE 2026 challenge; inference pipeline and three pretrained weights are released | Official inference/ensemble code and weights | **Medium–low.** Python 3.10/CUDA 12.8, FlashAttention/MMCV build order, three large checkpoints; try inference only after a dependency probe | Robustness reference and possible fallback reproduction |
| [DFD-HR](https://openaccess.thecvf.com/content/CVPR2026/papers/Sun_DFD-HR_Generalizable_Deepfake_Detection_via_Hierarchical_Routing_Learning_CVPR_2026_paper.pdf) / [code](https://github.com/Disguiser15/DFD-HR) | Hierarchical routing for visual foundation models: adaptive early-layer pruning, token selection using Spearman rank loss, and a unified mixture-of-experts design | Train on FaceForensics++; cross-dataset testing on Celeb-DF-v2 and other benchmarks; CLIP-L/14 checkpoint released | Official training/testing code, Apache-2.0, checkpoint, single-GPU command | **Medium.** Foundation backbone is heavy, but checkpoint-only evaluation is realistic on a Kaggle GPU with a small subset | Preferred first reproduction candidate |
| [VRAG-DFD](https://arxiv.org/abs/2604.13660) | Retrieve relevant forensic examples, then train an MLLM for critical reasoning through Alignment → SFT → GRPO | FKD and F-CoT datasets; generalization AUC and explanation-quality evaluation | Official repository is linked by the paper; full asset audit pending | **Low for full reproduction.** Multi-stage MLLM/RAG/RL training is beyond the first Kaggle milestone | Interpretability reference and future work |
| [Difficulty-Aware Domain-Incremental Learning](https://openaccess.thecvf.com/content/CVPR2026W/AIMS/html/Park_Efficient_Domain-Incremental_Deepfake_Detection_via_Difficulty-Aware_Curriculum_Learning_CVPRW_2026_paper.html) | Store easy/medium/hard samples in compact caches using entropy, feature distance, and diversity; train easy-to-hard with increasing augmentation and contrastive loss | DF40 plus Veo 3/Kling 2.5; 10 epochs, batch 64, one A5000; reports adaptation using 3% of new data | No official code URL was found in the paper during initial audit | **Low–medium.** Compute is plausible, but data volume and from-scratch continual-learning implementation are risky | Method reference; defer full reproduction |
| [WGN](https://openaccess.thecvf.com/content/CVPR2026W/PPMisDet/html/Ghosh_WGN_Wavelet-Guided_Network_for_Efficient_and_Generalised_Deepfake_Detection_CVPRW_2026_paper.html) | Differentiable Haar DWT creates frequency subbands that guide spatial attention through a lightweight WGSA module | FF++/FaceShifter in-domain and cross-dataset Celeb-DF, DFDC, WDF; 25 epochs on one RTX A2000 12 GB; 5.7M parameters and 3.7G FLOPs | No official code URL was found in the paper during initial audit | **Medium–high for a simplified reimplementation.** Resource profile fits Kaggle; reproduction risk comes from missing official code | Leading candidate for the later improvement phase |

## Completed detailed reviews

- [WGN: Wavelet-Guided Network for Efficient and Generalised Deepfake Detection](wgn-wavelet-guided-network.md) — methodology, results, ablations, limitations, and Kaggle reproduction scope reviewed on 2026-10-04.

## Provisional decision

1. Read **DFD-HR** and **WGN** in depth because they are closest to a feasible capstone experiment.
2. Use the **NTIRE** work to design corruption tests and understand ensemble robustness; do not begin with full three-stream training.
3. Use **VRAG-DFD** to discuss explainability and evidence-grounded outputs, not as the first baseline.
4. Use the **domain-incremental** paper to motivate adaptation to new generators; defer implementation unless the simpler baseline and dataset pipeline are already stable.

## Reproduction gate for Week 5

Attempt a small DFD-HR checkpoint evaluation only after all items pass:

- [ ] The dataset terms and access method are documented.
- [ ] The checkpoint downloads successfully in Kaggle.
- [ ] The environment imports on one Kaggle GPU.
- [ ] Ten samples run end to end.
- [ ] Output scores and labels can be exported to CSV.
- [ ] Runtime and peak GPU memory are recorded.

If dependency or memory failures cannot be resolved within one session, fall back to a maintained DeepfakeBench baseline and retain DFD-HR as an evaluation reference.

## Questions to answer while reading

- What is the exact train/test domain boundary?
- Is AUC image-level, frame-level, or video-level?
- Are face extraction and frame sampling identical across datasets?
- Which gains survive compression and cross-dataset transfer?
- Which component contributes the gain according to ablation?
- What data, checkpoints, or preprocessing steps are missing from the public repository?
- Which claim can be reproduced on one Kaggle GPU without changing the protocol?
