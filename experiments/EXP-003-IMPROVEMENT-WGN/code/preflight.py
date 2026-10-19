from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import common
from PIL import Image
from common import atomic_json, config_load, sha256
from data import build_datasets, external_datasets


def inspect(dataset, name, expected_videos=None, full_decode=True):
    videos = defaultdict(list)
    labels = Counter()
    for record in dataset.records:
        if not record.path.is_file():
            raise FileNotFoundError(f'{name}: {record.path}')
        videos[(record.manipulation, record.video)].append(record)
        labels[record.label] += 1
        if full_decode:
            with Image.open(record.path) as image:
                image.load()
                if min(image.size) < 8:
                    raise ValueError(f'Invalid image dimensions: {record.path}')
    if set(labels) != {0, 1}:
        raise ValueError(f'{name}: both classes are required')
    counts = Counter(group for group, video in videos)
    if expected_videos and any(count != expected_videos for count in counts.values()):
        raise ValueError(f'{name}: expected {expected_videos} videos per manipulation, found {counts}')
    if not full_decode:
        for records in videos.values():
            for record in (records[0], records[-1]):
                with Image.open(record.path) as image:
                    image.load()
    return {'frames': len(dataset), 'videos': len(videos), 'labels': dict(labels),
            'video_counts': dict(counts), 'full_image_decode': full_decode}


def check_training(config, full_decode=True):
    datasets = build_datasets(config)
    report = {}
    identities = []
    for split, expected, dataset in zip(('train','val','test'), (720,140,140), datasets):
        report[split] = inspect(dataset, split, expected, full_decode)
        identity = set()
        for record in dataset.records:
            identity.update(record.video.split('_'))
        identities.append(identity)
        for group in ('FF-real','FF-DF','FF-F2F','FF-FS','FF-NT'):
            if group not in report[split]['video_counts']:
                raise ValueError(f'Missing group {group}/{split}')
    if any(identities[i] & identities[j] for i,j in ((0,1),(0,2),(1,2))):
        raise ValueError('Source video identity overlaps across official splits')
    report['manifest_sha256'] = sha256(config['data']['json'])
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--sample-decode', action='store_true')
    args = parser.parse_args()
    config = config_load(args.config)
    report = check_training(config, not args.sample_decode)
    atomic_json(args.output, report)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
