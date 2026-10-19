# Celeb-DF v2 official-direct protocol

This control checks whether the current Celeb-DF result is sensitive to the
preprocessed DeepfakeBench RGB package.

- Source: the authors' Google Drive archive, file ID
  `1iLx76wsbi9itnkxSqz9BVBl4ZvnbIazj`, downloaded with the author's permission.
- Split: exactly the 518 entries in `List_of_testing_videos.txt` (178 real and
  340 fake videos). Labels are read from that file rather than inferred from
  paths.
- Sampling: 32 uniformly spaced frames per video.
- Face processing: the frozen WGN MTCNN path used for FF++, with detector size
  512, FP32, 256 x 256 crops, margin 0, largest-face selection, nearest detected
  box fallback, and center-crop fallback only when a video has no detections.
- Gate: one real and one fake video must pass extraction, full image decode,
  manifest loading, and a CUDA model forward pass before all 518 videos run.
- Evaluation: each completed improvement checkpoint is evaluated without
  target fine-tuning. The output is stored separately as
  `evaluation-celebdf-official-direct.json`.

Following the protocol diagnosis, the user selected official-direct as the
Celeb-DF v2 cross-data target for the improvement phase. Earlier DeepfakeBench
RGB measurements remain archived for provenance but are excluded from current
method comparisons and model selection.
