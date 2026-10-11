#!/usr/bin/env bash
set -uo pipefail

section() {
  printf '\n== %s ==\n' "$1"
}

section "Date and operating system"
date -Is 2>/dev/null || date
uname -a
if [[ -r /etc/os-release ]]; then
  sed -n '1,8p' /etc/os-release
fi

section "CPU, memory, and disk"
if command -v lscpu >/dev/null 2>&1; then
  lscpu | sed -n '1,12p'
fi
if command -v free >/dev/null 2>&1; then
  free -h
fi
df -h "$HOME" . 2>/dev/null || df -h .

section "GPU and driver"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi -L || true
  nvidia-smi --query-gpu=name,memory.total,driver_version,pci.bus_id --format=csv,noheader || true
else
  printf 'nvidia-smi not found\n'
fi

section "Development tools"
for tool in git conda micromamba python3; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s: %s\n' "$tool" "$(command -v "$tool")"
  else
    printf '%s: not found\n' "$tool"
  fi
done
git --version 2>/dev/null || true
conda --version 2>/dev/null || true
python3 --version 2>/dev/null || true

section "Python and PyTorch"
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import platform
import sys
print("Python executable:", sys.executable)
print("Python version:", platform.python_version())
try:
    import torch
    print("PyTorch:", torch.__version__)
    print("PyTorch CUDA build:", torch.version.cuda)
    print("CUDA available:", torch.cuda.is_available())
    print("GPU count:", torch.cuda.device_count())
    for index in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(index)
        print(
            f"GPU {index}: {props.name}; "
            f"capability {props.major}.{props.minor}; "
            f"VRAM {props.total_memory / (1024 ** 3):.1f} GiB"
        )
except Exception as exc:
    print("PyTorch check:", type(exc).__name__ + ":", exc)
PY
fi

printf '\nPreflight only: this script does not install packages, download data, or start training.\n'
