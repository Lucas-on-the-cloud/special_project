#!/usr/bin/env bash
# Read-only diagnostic for the Linux lab machine.
# It does not install packages, change files, or access project data.

set -u

section() {
  printf '\n===== %s =====\n' "$1"
}

section "Operating system"
uname -a
if [[ -r /etc/os-release ]]; then
  cat /etc/os-release
fi

section "NVIDIA GPU"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi is not installed or no NVIDIA driver is available."
fi

section "Python and PyTorch"
if command -v python3 >/dev/null 2>&1; then
  python3 --version
  python3 - <<'PY'
import importlib.util
import sys

print("Python executable:", sys.executable)
if importlib.util.find_spec("torch") is None:
    print("PyTorch: not installed in this Python environment")
else:
    try:
        import torch
        print("PyTorch:", torch.__version__)
        print("CUDA available to PyTorch:", torch.cuda.is_available())
        print("PyTorch CUDA build:", torch.version.cuda)
        print("GPU count:", torch.cuda.device_count())
        for index in range(torch.cuda.device_count()):
            print(f"GPU {index}:", torch.cuda.get_device_name(index))
    except Exception as exc:
        print("PyTorch import failed:", repr(exc))
PY
else
  echo "python3 is not installed or is not on PATH."
fi

section "Git and environment managers"
for tool in git conda mamba micromamba uv; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s: ' "$tool"
    "$tool" --version 2>&1 | head -n 1
  else
    printf '%s: not found\n' "$tool"
  fi
done

section "Diagnostic complete"
echo "This script only reports system information; it does not install or modify anything."
