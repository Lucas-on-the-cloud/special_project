# Cross-manipulation decision

On 20 October 2026, the selected-candidate cross-manipulation sweep was deferred
until a future architecture modification is ready for comparison.

The completed degradation experiments already establish a useful signal:
degradation augmentation without the consistency penalty is the strongest
current candidate under the locked cross-dataset protocol. Running four new
25-epoch manipulation-specific models now would spend substantial compute on an
architecture that is expected to change.

The `degradation_control` model trained on DF completed 11 of 25 epochs before
the runner was intentionally stopped. Its `last.pt`, current `best.pt`, resolved
config, metrics, and environment record remain in the local runtime directory
`C:/sp/runs/wgn_overnight/cross_degradation_control_df_final/`. This partial run
is not a final experiment, is not included in result tables, and is not uploaded
as a selected checkpoint.

When the next architecture candidate is frozen, rerun the same four training
groups (DF, F2F, FS, and NT) for both the chosen reference and new candidate,
then report the full 4 × 4 matrix, mean including the diagonal, and unseen-only
mean. Do not combine the partial 11-epoch DF run with future 25-epoch results.
