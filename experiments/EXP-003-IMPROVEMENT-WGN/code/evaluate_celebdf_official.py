"""Evaluate a completed WGN run on directly prepared official Celeb-DF v2 videos."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import common
import torch

from common import atomic_json, config_load, make_model, sha256
from data import FaceForensicsJsonDataset, build_binary_dataset_records
from preflight import inspect
from prepare_celebdf_official import DATASET, REAL_GROUP, FAKE_GROUP, MANIFEST, SOURCE
from train import evaluate, loader


DATA = Path('C:/sp/data')


def evaluate_run(run):
    run = Path(run)
    if not (run/'summary.json').is_file() or not (run/'best.pt').is_file():
        raise FileNotFoundError(f'Completed final run required: {run}')
    config = config_load(run/'resolved_config.yaml')
    records = build_binary_dataset_records(MANIFEST, DATA, DATASET, REAL_GROUP, FAKE_GROUP)
    dataset = FaceForensicsJsonDataset(records, train=False)
    inspect(dataset, DATASET, expected_videos=None, full_decode=False)
    if len({record.video for record in records}) != 518 or {record.label for record in records} != {0,1}:
        raise ValueError('Official Celeb-DF dataset must contain 518 videos and both classes')
    identity = hashlib.sha256(json.dumps([(str(r.path),r.label,r.manipulation,r.video)
                                          for r in records]).encode()).hexdigest()
    output = run/'evaluation-celebdf-official-direct.json'
    checkpoint_sha = sha256(run/'best.pt')
    if output.exists():
        old = json.loads(output.read_text())
        if old['checkpoint_sha256'] != checkpoint_sha or old['record_sha256'] != identity:
            raise ValueError('Refusing to overwrite locked official Celeb-DF evaluation')
        return old
    model = make_model(config, pretrained=False).cuda().eval()
    model.load_state_dict(torch.load(run/'best.pt', map_location='cpu', weights_only=False)['model'])
    measured = evaluate(model, loader(dataset, config))
    preprocessing = json.loads((SOURCE/'preprocessing.json').read_text())
    result = {'checkpoint_sha256': checkpoint_sha, 'record_sha256': identity,
              'protocol': 'official author videos -> uniform 32 frames -> WGN MTCNN crop',
              'preprocessing': preprocessing, 'metrics': measured}
    atomic_json(output, result)
    print('EVALUATED_OFFICIAL_CELEBDF '+json.dumps(measured), flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    evaluate_run(parser.parse_args().run)
