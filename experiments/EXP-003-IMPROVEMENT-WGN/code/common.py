from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import random
import sys
import tempfile
import time

import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'reproduction' / 'code'
sys.path.insert(0, str(BASE / 'src'))


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False


def _replace_with_retry(source, destination, attempts=20):
    """Tolerate short-lived Windows reader/antivirus locks on status files."""
    for attempt in range(attempts):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt + 1 == attempts:
                raise
            time.sleep(min(0.01 * (attempt + 1), 0.25))


def atomic_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False), encoding='utf-8')
    _replace_with_retry(temporary, path)


def atomic_save(path, payload):
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    torch.save(payload, temporary)
    _replace_with_retry(temporary, path)


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def config_load(path):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8'))


def make_model(config, pretrained=None):
    from models import GradientWGN
    from wgn.model import WaveletGuidedNetwork
    setting = config['model']
    cls = GradientWGN if config['method'] == 'gradient' else WaveletGuidedNetwork
    return cls(pretrained=setting['pretrained'] if pretrained is None else pretrained,
               backbone_name=setting['backbone'], gate_hidden_dim=setting['gate_hidden_dim'])
