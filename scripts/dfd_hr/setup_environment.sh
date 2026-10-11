#!/usr/bin/env bash
set -euo pipefail

readonly UPSTREAM_URL="https://github.com/Disguiser15/DFD-HR.git"
readonly UPSTREAM_COMMIT="ec85fc462d06f06448d2222748e24e7113f25784"
readonly ENV_NAME="dfdhr-py310"
readonly REPO_DIR="$HOME/DFD-HR"

if ! command -v git >/dev/null 2>&1; then
  printf 'ERROR: git is required. Run the cloud preflight first.\n' >&2
  exit 1
fi

if ! command -v conda >/dev/null 2>&1; then
  printf 'ERROR: conda is not available. Stop here and share the preflight output before installing anything.\n' >&2
  exit 1
fi

if [[ -d "$REPO_DIR/.git" ]]; then
  origin_url="$(git -C "$REPO_DIR" remote get-url origin)"
  if [[ "$origin_url" != "$UPSTREAM_URL" && "$origin_url" != "https://github.com/Disguiser15/DFD-HR" ]]; then
    printf 'ERROR: %s exists but is not the official DFD-HR clone. No files were changed.\n' "$REPO_DIR" >&2
    exit 1
  fi
  if [[ -n "$(git -C "$REPO_DIR" status --porcelain)" ]]; then
    printf 'ERROR: %s has uncommitted changes. No files were changed.\n' "$REPO_DIR" >&2
    exit 1
  fi
  git -C "$REPO_DIR" fetch origin "$UPSTREAM_COMMIT"
  git -C "$REPO_DIR" checkout --detach "$UPSTREAM_COMMIT"
else
  if [[ -e "$REPO_DIR" ]]; then
    printf 'ERROR: %s exists and is not a Git clone. No files were changed.\n' "$REPO_DIR" >&2
    exit 1
  fi
  git clone "$UPSTREAM_URL" "$REPO_DIR"
  git -C "$REPO_DIR" checkout --detach "$UPSTREAM_COMMIT"
fi

actual_commit="$(git -C "$REPO_DIR" rev-parse HEAD)"
if [[ "$actual_commit" != "$UPSTREAM_COMMIT" ]]; then
  printf 'ERROR: expected upstream commit %s but found %s\n' "$UPSTREAM_COMMIT" "$actual_commit" >&2
  exit 1
fi
printf 'Official DFD-HR commit: %s\n' "$actual_commit"

if ! conda env list | awk 'NR > 2 {print $1}' | grep -Fxq "$ENV_NAME"; then
  conda create --yes --name "$ENV_NAME" python=3.10.15
else
  python_version="$(conda run --no-capture-output -n "$ENV_NAME" python --version 2>&1)"
  if [[ "$python_version" != "Python 3.10.15" ]]; then
    printf 'ERROR: environment %s exists with %s; expected Python 3.10.15.\n' "$ENV_NAME" "$python_version" >&2
    exit 1
  fi
fi

conda run --no-capture-output -n "$ENV_NAME" python -m pip install --upgrade pip==23.1
conda run --no-capture-output -n "$ENV_NAME" python -m pip install -r "$REPO_DIR/requirements.txt"

conda run --no-capture-output -n "$ENV_NAME" python - <<'PY'
import torch
import torchvision
import transformers
print("Python / package check passed")
print("PyTorch:", torch.__version__)
print("Torchvision:", torchvision.__version__)
print("Transformers:", transformers.__version__)
print("CUDA build:", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())
print("GPU count:", torch.cuda.device_count())
for index in range(torch.cuda.device_count()):
    print(f"GPU {index}: {torch.cuda.get_device_name(index)}")
if not torch.cuda.is_available():
    raise SystemExit("CUDA is unavailable in this environment.")
PY

printf '\nEnvironment setup complete. No dataset or DFD-HR checkpoint was downloaded.\n'
