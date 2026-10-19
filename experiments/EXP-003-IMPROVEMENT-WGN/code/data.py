from __future__ import annotations

from collections import defaultdict
from io import BytesIO
from pathlib import Path
import random

import common
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms
from wgn.data import FaceForensicsJsonDataset, build_datasets, build_binary_dataset_records


OFFICIAL_CELEB = {
    'dataset': 'Celeb-DF-v2-official-direct',
    'display_name': 'Celeb-DF-v2 official-direct',
    'root': 'C:/sp/data',
    'json': 'C:/sp/data/Celeb-DF-v2-official-direct.json',
    'real_group': 'CelebDFv2Official_real',
    'fake_group': 'CelebDFv2Official_fake',
}


class PairedDataset(Dataset):
    def __init__(self, dataset):
        self.dataset = dataset
        self.groups = defaultdict(list)
        for index, record in enumerate(dataset.records):
            self.groups[(record.manipulation, record.video, record.label)].append(index)
        if any(len(indices) < 2 for indices in self.groups.values()):
            raise ValueError('Temporal training requires two distinct frames in every video')
        self.offsets = {}
        for indices in self.groups.values():
            for position, index in enumerate(indices):
                self.offsets[index] = position

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index):
        first = self.dataset[index]
        record = self.dataset.records[index]
        candidates = self.groups[(record.manipulation, record.video, record.label)]
        # Offset sampling excludes the anchor without a rejection loop.
        position = (self.offsets[index] + random.randrange(1, len(candidates))) % len(candidates)
        partner = self.dataset[candidates[position]]
        first['image_pair'] = partner['image']
        first['path_pair'] = partner['path']
        return first


class RandomJpegCompression:
    def __init__(self, quality_min=30, quality_max=95):
        self.quality_min = quality_min
        self.quality_max = quality_max

    def __call__(self, image):
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=random.randint(self.quality_min, self.quality_max),
                   subsampling=2)
        buffer.seek(0)
        with Image.open(buffer) as decoded:
            return decoded.convert('RGB')


class RandomDownscale:
    def __init__(self, scale_min=.5, scale_max=1.):
        self.scale_min = scale_min
        self.scale_max = scale_max

    def __call__(self, image):
        width, height = image.size
        scale = random.uniform(self.scale_min, self.scale_max)
        small = image.resize((max(8, round(width*scale)), max(8, round(height*scale))),
                             Image.Resampling.BILINEAR)
        return small.resize((width, height), Image.Resampling.BILINEAR)


class DegradationPairDataset(Dataset):
    """Return a standard source view and an independently degraded source view."""
    def __init__(self, dataset, config):
        self.dataset = dataset
        self.records = dataset.records
        setting = config['degradation']
        size = int(config['data']['image_size'])
        self.clean = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
        ])
        self.degraded = transforms.Compose([
            transforms.Resize((size, size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomAffine(degrees=0, translate=(setting['crop_jitter'], setting['crop_jitter']),
                                    scale=(1-setting['crop_jitter'], 1.0)),
            transforms.RandomApply([RandomDownscale(setting['downscale_min'], 1.)],
                                   p=setting['downscale_probability']),
            transforms.RandomApply([RandomJpegCompression(setting['jpeg_quality_min'],
                                                            setting['jpeg_quality_max'])],
                                   p=setting['jpeg_probability']),
            transforms.RandomApply([transforms.GaussianBlur(3, sigma=(.1, setting['blur_sigma_max']))],
                                   p=setting['blur_probability']),
            transforms.RandomApply([transforms.ColorJitter(brightness=setting['color_jitter'],
                                                             contrast=setting['color_jitter'],
                                                             saturation=setting['color_jitter']*.75,
                                                             hue=.02)],
                                   p=setting['color_probability']),
            transforms.ToTensor(),
        ])

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        record = self.records[index]
        with Image.open(record.path) as source:
            image = source.convert('RGB')
            clean = self.clean(image)
            degraded = self.degraded(image)
        return {'image': clean, 'image_pair': degraded,
                'label': torch.tensor(record.label, dtype=torch.float32),
                'video': record.video, 'manipulation': record.manipulation,
                'path': str(record.path), 'path_pair': str(record.path),
                'pair_kind': 'source_degradation'}


def curriculum_indices(ranking, records, fraction):
    """Retain the easy fraction WITHIN each class/manipulation to avoid class collapse."""
    groups = defaultdict(list)
    for index, record in enumerate(records):
        groups[(record.label, record.manipulation)].append(index)
    selected = []
    for indices in groups.values():
        ordered = sorted(indices, key=lambda i: (ranking[i], str(records[i].path)))
        selected.extend(ordered[:max(1, int(len(ordered) * fraction))])
    return selected


def fraction_for_epoch(epoch):
    return 0.5 if epoch < 8 else 0.75 if epoch < 16 else 1.0


def external_datasets(config):
    for target in config.get('external', []):
        # Celeb-DF is always evaluated from the authors' videos prepared by WGN.
        # Training configs retain their frozen provenance so resumable checkpoints
        # are not invalidated by this evaluation-only protocol change.
        target = OFFICIAL_CELEB if target['dataset'] == 'Celeb-DF-v2' else target
        records = build_binary_dataset_records(Path(target['json']), Path(target['root']),
                    target['dataset'], target['real_group'], target['fake_group'], split='test')
        yield target.get('display_name', target['dataset']), FaceForensicsJsonDataset(records, train=False)
