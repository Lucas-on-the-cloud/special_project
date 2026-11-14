# EXP-004 V2: per-video and per-manipulation postprocessing

The EXP-002 frame-level reference is based on multiple frames of the same source video; frames are not independent observations. The V2 runner outputs per-frame predictions, source-video IDs and manipulation group.

After each successful run, execute:

```bash
python experiments/EXP-004-ADVERSARIAL-WGN/code/analyze_by_video.py \
  --run "$WGN_REPO_ROOT/exp04_runs/full_c23_seed1024" \
  --method jia-faa-adapt --bootstrap 1000
```

Repeat for `fgsm` and `pgd`.

The output `jia-faa-adapt_video_analysis.json` contains:
- frame conditional Fake→Real ASR and percentile cluster-bootstrap 95% interval;
- conditional fake ASR per manipulation group (FF-DF, FF-F2F, FF-FS, FF-NT);
- video-level clean AUC and attacked-fake/clean-real AUC (mean frame scores per [manipulation, video, label]);
- video-level fake ASR on originally correctly classified fake videos.

**Caution**: As the fake counterpart video may share a real source-video identity, video grouping by the manifest `video` ID is an approximation to source-identity clustering. A later audit should use the official FF++ pair mappings to prevent underestimating dependence; treat confidence intervals as exploratory until that is done.

Report both the numerator and denominator of conditional ASR. Do not claim WGN WGSA is a causal vulnerability solely from gate drift. Stronger attack restarts and matched, trained backbone ablations remain follow-up steps.
