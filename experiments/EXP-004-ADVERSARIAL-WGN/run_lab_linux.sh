#!/usr/bin/env bash
set -euo pipefail

: "${WGN_REPO_ROOT:?Set WGN_REPO_ROOT to cloned special_project directory}"
: "${WGN_DATA_ROOT:?Set WGN_DATA_ROOT to restored processed dataset root}"
: "${WGN_CHECKPOINT:?Set WGN_CHECKPOINT to SHA-verified EXP-002 baseline_final/best.pt}"

EXP_ROOT="${WGN_REPO_ROOT}/experiments/EXP-004-ADVERSARIAL-WGN"
MANIFEST="${WGN_MANIFEST:-${WGN_DATA_ROOT}/FaceForensics++-official.json}"
RUN_ROOT="${WGN_RUN_ROOT:-${WGN_REPO_ROOT}/exp04_runs}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
PILOT_DIR="${WGN_OUTPUT:-${RUN_ROOT}/v2_pilot_${STAMP}}"
CLEAN_JSON="${RUN_ROOT}/clean_reference_${STAMP}.json"

mkdir -p "$RUN_ROOT"

echo "== T2: environment/artifact preflight =="
python "${EXP_ROOT}/code/lab_preflight.py"   --repo-root "$WGN_REPO_ROOT"   --checkpoint "$WGN_CHECKPOINT"   --manifest "$MANIFEST"   --data-root "$WGN_DATA_ROOT"

echo "== T1: CPU/unit correctness tests =="
python -m pytest "${EXP_ROOT}/tests" -q

echo "== T3: mandatory clean EXP-002 continuity gate =="
python "${EXP_ROOT}/code/validate_clean_reference.py"   --repo-root "$WGN_REPO_ROOT"   --checkpoint "$WGN_CHECKPOINT"   --manifest "$MANIFEST"   --data-root "$WGN_DATA_ROOT"   --output "$CLEAN_JSON"

echo "== T4: small adversarial CUDA smoke test (NOT a research result) =="
python "${EXP_ROOT}/code/run_exp04_v2.py"   --repo-root "$WGN_REPO_ROOT"   --checkpoint "$WGN_CHECKPOINT"   --manifest "$MANIFEST"   --data-root "$WGN_DATA_ROOT"   --expected-checkpoint-sha256 a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6   --output "$PILOT_DIR"   --max-samples 40   --batch-size 4   --steps 3

echo
echo "PILOT_COMPLETE"
echo "Clean gate: $CLEAN_JSON"
echo "Pilot:      $PILOT_DIR"
echo "Do NOT start the locked full test until TEST_PLAN.md T5 is reviewed."
