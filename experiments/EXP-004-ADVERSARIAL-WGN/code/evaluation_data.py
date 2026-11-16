"""Locked WGN input adapters and portable cohort identity for EXP-004."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PureWindowsPath
import sys

EXTERNAL_DATASETS = {
    'dfdc': ('DFDC', 'DFDC_Real', 'DFDC_Fake', 'DFDC'),
    'celebdf': ('Celeb-DF-v2-official-direct', 'CelebDFv2Official_real',
                'CelebDFv2Official_fake', 'Celeb-DF-v2 official-direct'),
    'wilddeepfake': ('WildDeepfake', 'WildDeepfake_Real', 'WildDeepfake_Fake', 'WildDeepfake'),
}
DATASETS = ('ffpp', *EXTERNAL_DATASETS)


def load_source(repo_root):
    source = Path(repo_root)/'experiments/EXP-002-WGN/reproduction/code/src'
    if not source.is_dir():
        raise FileNotFoundError(source)
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))


def load_records(repo_root, manifest, data_root, config, dataset, split='test', compression='c23'):
    load_source(repo_root)
    from wgn.data import build_records, build_binary_dataset_records
    if dataset == 'ffpp':
        data = config['data']
        records = build_records(Path(manifest), Path(data_root), split,
            int(data['frames_per_real']), int(data['frames_per_fake']),
            tuple(data['manipulations']), compression)
    elif dataset in EXTERNAL_DATASETS:
        name, real, fake, _ = EXTERNAL_DATASETS[dataset]
        records = build_binary_dataset_records(Path(manifest), Path(data_root),
            name, real, fake, split=split)
    else:
        raise ValueError('Unknown dataset: '+dataset)
    if not records or {r.label for r in records} != {0, 1}:
        raise ValueError('A nonempty binary cohort is required')
    root = Path(data_root).resolve()
    paths = []
    for record in records:
        path = record.path.resolve()
        path.relative_to(root)
        paths.append(path)
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate frame paths in cohort')
    return records


def cohort_fingerprint(records, data_root, *, windows_reference=False):
    root = Path(data_root).resolve()
    rows = []
    for record in records:
        relative = record.path.resolve().relative_to(root)
        path = str(PureWindowsPath('C:/sp/data').joinpath(*relative.parts)) if windows_reference else relative.as_posix()
        rows.append((path, record.label, record.manipulation, record.video))
    return hashlib.sha256(json.dumps(rows).encode()).hexdigest()


def reference_target(repo_root, dataset, compression='c23'):
    artifact = Path(repo_root)/'experiments/EXP-002-WGN/reproduction/artifacts/baseline_final/evaluation.json'
    targets = json.loads(artifact.read_text())['datasets']
    return targets[EXTERNAL_DATASETS[dataset][3] if dataset in EXTERNAL_DATASETS else f'FF++ {compression}']


def ffpp_pair_mapping(repo_root, split):
    path = Path(repo_root)/f'experiments/EXP-002-WGN/reproduction/code/splits/{split}.json'
    pairs = json.loads(path.read_text())
    mapping = {}
    for pair in pairs:
        cluster = 'ffpp-pair:' + '_'.join(sorted(pair))
        for video in pair:
            if video in mapping and mapping[video] != cluster:
                raise ValueError('FF++ source identity occurs in different pair clusters')
            mapping[video] = cluster
    return mapping


def source_cluster(video, dataset, pair_mapping):
    if dataset in EXTERNAL_DATASETS:
        return dataset+'-video:'+video
    members = video.split('_')
    clusters = {pair_mapping[member] for member in members}
    if len(clusters) != 1:
        raise ValueError('Fake video members belong to different official source pairs')
    return clusters.pop()
