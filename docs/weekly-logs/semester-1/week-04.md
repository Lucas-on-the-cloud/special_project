# Semester 1 — Week 04 — Paper Triage and Reproduction Selection

**Date started:** 2026-10-02  
**Status:** In progress

## Advisor request

Review five 2026 sources covering robust ensembles, hierarchical routing, retrieval-augmented MLLMs, domain-incremental curriculum learning, and wavelet-guided detection.

## Checklist

### Reading

- [ ] NTIRE 2026 robust ensemble: method, degradation engine, ensemble, limitations.
- [ ] DFD-HR: layer routing, token routing, MoE, datasets, ablations.
- [ ] VRAG-DFD: retrieval database, F-CoT, Alignment/SFT/GRPO, explanation evaluation.
- [ ] Domain-incremental curriculum: cache construction, curriculum, forgetting/generalization protocol.
- [ ] WGN: Haar DWT, WGSA, complexity, compression and cross-dataset results.

### Reproducibility audit

- [x] Verify the official paper/repository links.
- [x] Record public code and checkpoint status.
- [x] Record reported datasets, compute, and primary metrics where available.
- [x] Classify likely Kaggle feasibility.
- [ ] Verify dataset access and license for the selected smoke test.
- [ ] Confirm the Week 5 target and fallback.

### Weekly output

- [x] Create the five-source comparison matrix.
- [ ] Write one structured note per source in the student's own words.
- [ ] Record final Week 4 conclusions and unresolved questions.
- [ ] Prepare the Week 5 Kaggle smoke-test checklist; no full training yet.

## Initial triage decision

- **Preferred first reproduction:** DFD-HR pretrained checkpoint evaluation.
- **Fallback/reference:** NTIRE inference pipeline if dependencies and weights fit Kaggle.
- **Likely later improvement:** simplified WGN-style wavelet-guided attention.
- **Background/future work:** VRAG-DFD and domain-incremental curriculum learning.

This decision remains provisional until the Kaggle dependency, memory, and dataset checks pass.

## End-of-week questions

1. Which exact dataset subset can be accessed and documented?
2. Is the baseline output image-, frame-, or video-level AUC?
3. Can a clean Kaggle session reproduce predictions from released weights?
4. What is the smallest experiment that tests a real claim from the selected paper?
5. Which missing dependency, preprocessing step, or data license could block reproduction?
