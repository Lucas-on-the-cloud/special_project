# Semester 1 — Week 02 — Bias and Generalization

**Status:** Completed and reconstructed from the Week 3 progress report

## Completed

- [x] Reviewed demographic and visual-attribute bias in common deepfake datasets.
- [x] Reviewed spectral shortcut learning and failure on unseen generators.
- [x] Studied FreqDebias: frequency-band identification, amplitude scrambling, and consistency constraints.
- [x] Studied UCF as a generalizable deepfake detection reference.
- [x] Reviewed a fairness framework based on structural decoupling and distribution alignment.

## Main conclusion

The capstone should not claim success from one random in-dataset split. The evaluation should include cross-dataset or cross-manipulation performance, corruption robustness, and subgroup metrics only where trustworthy metadata exists.

## Candidate measurements

- AUC and accuracy under the exact selected protocol
- False-positive and false-negative rates
- Cross-dataset AUC gap
- Performance change under compression/resize/blur
- Subgroup AUC/FPR/FNR gap when valid demographic annotations are available
