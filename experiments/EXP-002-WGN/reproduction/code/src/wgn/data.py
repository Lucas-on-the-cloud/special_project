from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Iterable

from PIL import Image
import torch
from torch.utils.data import Dataset
from torchvision import transforms


FAKE_LABELS = ("FF-DF", "FF-F2F", "FF-FS", "FF-NT")


@dataclass(frozen=True)
class FrameRecord:
    path: Path
    label: int
    video: str
    manipulation: str


def _even_sample(items: list[str], count: int) -> list[str]:
    if count <= 0 or len(items) <= count:
        return items
    if count == 1:
        return [items[len(items) // 2]]
    indices = [round(index * (len(items) - 1) / (count - 1)) for index in range(count)]
    return [items[index] for index in indices]


def _local_path(data_root: Path, relative: str) -> Path:
    return data_root.joinpath(*PureWindowsPath(relative).parts)


def build_records(
    json_path: Path,
    data_root: Path,
    split: str,
    frames_per_real: int,
    frames_per_fake: int,
    manipulations: Iterable[str] = FAKE_LABELS,
    compression: str = "c23",
) -> list[FrameRecord]:
    with json_path.open("r", encoding="utf-8") as handle:
        root = json.load(handle)["FaceForensics++"]

    records: list[FrameRecord] = []
    groups = [("FF-real", 0), *((name, 1) for name in manipulations)]
    for group, binary_label in groups:
        videos = root[group][split][compression]
        requested = frames_per_real if binary_label == 0 else frames_per_fake
        for video_name, metadata in videos.items():
            for relative_path in _even_sample(metadata["frames"], requested):
                records.append(
                    FrameRecord(
                        path=_local_path(data_root, relative_path),
                        label=binary_label,
                        video=video_name,
                        manipulation=group,
                    )
                )
    return records


def build_binary_dataset_records(
    json_path: Path,
    data_root: Path,
    dataset_name: str,
    real_group: str,
    fake_group: str,
    split: str = "test",
    frames_per_video: int = 0,
) -> list[FrameRecord]:
    """Read a DeepfakeBench-style JSON dataset without a compression level."""
    with json_path.open("r", encoding="utf-8") as handle:
        root = json.load(handle)[dataset_name]

    records: list[FrameRecord] = []
    for group, binary_label in ((real_group, 0), (fake_group, 1)):
        for video_name, metadata in root[group][split].items():
            frames = metadata["frames"]
            selected = _even_sample(frames, frames_per_video) if frames_per_video > 0 else frames
            for relative_path in selected:
                records.append(
                    FrameRecord(
                        path=_local_path(data_root, relative_path),
                        label=binary_label,
                        video=video_name,
                        manipulation=group,
                    )
                )
    return records


class FaceForensicsJsonDataset(Dataset):
    def __init__(self, records: list[FrameRecord], train: bool, image_size: int = 256) -> None:
        self.records = records
        operations: list[object] = [transforms.Resize((image_size, image_size))]
        if train:
            # The paper does not disclose augmentation; horizontal flip is an explicit assumption.
            operations.append(transforms.RandomHorizontalFlip())
        operations.extend([transforms.ToTensor()])
        self.transform = transforms.Compose(operations)

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> dict[str, object]:
        record = self.records[index]
        with Image.open(record.path) as image:
            tensor = self.transform(image.convert("RGB"))
        return {
            "image": tensor,
            "label": torch.tensor(record.label, dtype=torch.float32),
            "video": record.video,
            "manipulation": record.manipulation,
            "path": str(record.path),
        }


def build_datasets(config: dict) -> tuple[FaceForensicsJsonDataset, FaceForensicsJsonDataset, FaceForensicsJsonDataset]:
    data_root = Path(config["data"]["root"])
    json_path = Path(config["data"]["json"])
    kwargs = {
        "json_path": json_path,
        "data_root": data_root,
        "frames_per_real": int(config["data"]["frames_per_real"]),
        "frames_per_fake": int(config["data"]["frames_per_fake"]),
        "manipulations": tuple(config["data"].get("manipulations", FAKE_LABELS)),
        "compression": str(config["data"].get("compression", "c23")),
    }
    train = FaceForensicsJsonDataset(build_records(split="train", **kwargs), train=True)
    val = FaceForensicsJsonDataset(build_records(split="val", **kwargs), train=False)
    test = FaceForensicsJsonDataset(build_records(split="test", **kwargs), train=False)
    return train, val, test


def seed_worker(worker_id: int) -> None:
    worker_seed = torch.initial_seed() % 2**32
    random.seed(worker_seed + worker_id)

