# EXP-004 isolated laboratory environment

The runtime directory is outside the Git checkout:

```bash
cd /home/naeem/Downloads/s1123570_sp1
uv venv --python /home/naeem/.pyenv/versions/3.11.14/bin/python exp04-runtime/venv \
  --cache-dir exp04-runtime/uv-cache

uv pip install --python exp04-runtime/venv/bin/python \
  --cache-dir exp04-runtime/uv-cache \
  --index-url https://download.pytorch.org/whl/cu128 \
  torch==2.7.1 torchvision==0.22.1

uv pip install --python exp04-runtime/venv/bin/python \
  --cache-dir exp04-runtime/uv-cache \
  -r special_project/experiments/EXP-004-ADVERSARIAL-WGN/code/requirements-lab.txt

exp04-runtime/venv/bin/python -m pytest \
  special_project/experiments/EXP-004-ADVERSARIAL-WGN/tests -q
```

The Python patch version is 3.11.14 rather than the archived Windows baseline's 3.11.9; record it with the operating-system/GPU differences. Main numerical package versions follow the baseline artifact. `scipy`, `pytest` and the Hugging Face client are explicitly pinned for verification/restore tooling. Freeze all resolved dependencies after successful installation.

Face crops are restored from the existing backup; the conflicting combined preprocessing requirements are not installed into this environment. Installation and CPU tests establish software readiness, not attack fidelity or clean-reference continuity. Check `JIA-ALGORITHM-SPEC.md` and `PLAN.md` before GPU evaluation.
