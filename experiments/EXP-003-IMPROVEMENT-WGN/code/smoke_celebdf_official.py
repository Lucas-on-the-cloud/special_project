"""Smoke the official Celeb-DF manifest through the real input and model pipeline."""
from __future__ import annotations

import argparse
from pathlib import Path

import common
import torch

from common import atomic_json, config_load, make_model
from data import FaceForensicsJsonDataset, build_binary_dataset_records
from preflight import inspect
from prepare_celebdf_official import DATA, DATASET, REAL_GROUP, FAKE_GROUP
from train import loader


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = config_load(args.config)
    records = build_binary_dataset_records(args.manifest, DATA, DATASET, REAL_GROUP, FAKE_GROUP)
    dataset = FaceForensicsJsonDataset(records, train=False)
    report = inspect(dataset, DATASET, expected_videos=None, full_decode=True)
    if report['videos'] != 2 or {record.label for record in records} != {0, 1}:
        raise ValueError(f'Official smoke requires exactly one real and one fake video: {report}')
    model = make_model(config, pretrained=False).cuda().eval()
    batch = next(iter(loader(dataset, config)))
    with torch.no_grad():
        logits = model(batch['image'].cuda(non_blocking=True))
    if not torch.isfinite(logits).all():
        raise FloatingPointError('Non-finite official Celeb-DF smoke logits')
    result = {'status': 'passed', 'preflight': report, 'logits_checked': len(logits)}
    atomic_json(args.output, result)
    print(result, flush=True)


if __name__ == '__main__':
    main()
