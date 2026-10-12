# DFD-HR Stage 1 Reproduction Status

Date: 2026-10-12 (Asia/Bangkok)

## Scope

- Train DFD-HR on FaceForensics++ c23.
- Validate on Celeb-DF-v2.
- Cross-dataset and cross-manipulation evaluations are deferred until the main training setup is confirmed.

## Verified inputs

- Official DFD-HR source archive was used as the baseline.
- All 159,626 FaceForensics++ frame paths referenced by the repository JSON were present.
- All 222,141 Celeb-DF-v2 frame paths referenced by the repository JSON were present.
- Backbone: pretrained `openai/clip-vit-large-patch14`; CLIP parameters are frozen by the official detector code.

## Official-checkpoint baseline

Evaluation of the released checkpoint on Celeb-DF-v2 with the public repository's 8-frame test configuration produced:

- Video AUC: 0.9382518176
- Video EER: 0.1404494382
- Video accuracy: 0.8552123552

The paper reports a Celeb-DF-v2 video AUC of 0.960 and states that 32 frames are used at inference, while the public YAML specifies 8 test frames.

## RTX 5090 timing run

- GPU: NVIDIA GeForce RTX 5090, 32,607 MiB reported VRAM.
- Precision: FP32.
- Physical batch size: 4.
- Gradient accumulation: 4.
- Effective batch size: 16.
- DataLoader workers: 8.
- Epoch size: 7,192 micro-batches (28,768 samples).
- Stopped at: 1,079 / 7,192 micro-batches (15%).
- Elapsed training-loop time: 1:25:08.
- Observed iteration time: approximately 4.7-4.8 seconds.
- Projected training time: approximately 9-10 hours per epoch and 8-9 days for 20/21 epochs, excluding full validation overhead.
- Sampled GPU utilization: generally 10-30%, with approximately 22 GiB VRAM in use during training.

The process was intentionally stopped before completing epoch 0. No training checkpoint was produced. Logs were preserved.

## Reproduction ambiguities

1. The paper does not specify the GPU model/count or training precision.
2. It is unclear whether batch size 16 is global or per GPU. The official launcher uses four processes while retaining `train_batchSize: 16`.
3. The YAML specifies `nEpochs: 20`, but the loop uses `range(start_epoch, nEpochs + 1)`, apparently executing epochs 0-20.
4. The paper states 32 inference frames, while the public YAML uses 8.
5. The public loader's frame-selection logic appears not to evenly sample the complete list of available frames.

## Proposed next step

Keep the official setup as the audit baseline, then benchmark an algorithmically faithful implementation using BF16, epoch-level metrics, improved data loading, and vectorized routing. If strict FP32 reproduction is required, use the official four-GPU launch pattern and confirm the global batch interpretation with the authors.
