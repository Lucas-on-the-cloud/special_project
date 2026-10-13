from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


MANIFEST = Path(r"C:\sp1\data\FaceForensics++-official.json")
DATA_ROOT = MANIFEST.parent
GROUPS = ("FF-real", "FF-DF", "FF-F2F", "FF-FS", "FF-NT", "FF-FSh")
COMPRESSIONS = ("c23", "c40")
EXPECTED_VIDEOS = {"train": 720, "val": 140, "test": 140}


def main() -> int:
    with MANIFEST.open("r", encoding="utf-8") as handle:
        root = json.load(handle)["FaceForensics++"]

    paths: list[Path] = []
    for group in GROUPS:
        expected_frames = 40 if group == "FF-real" else 10
        for compression in COMPRESSIONS:
            for split, expected_videos in EXPECTED_VIDEOS.items():
                videos = root[group][split][compression]
                if len(videos) != expected_videos:
                    raise RuntimeError(
                        f"{group}/{compression}/{split}: expected {expected_videos} videos, "
                        f"got {len(videos)}"
                    )
                for video, record in videos.items():
                    frames = record["frames"]
                    if len(frames) != expected_frames:
                        raise RuntimeError(
                            f"{group}/{compression}/{split}/{video}: expected "
                            f"{expected_frames} frames, got {len(frames)}"
                        )
                    paths.extend(
                        path if path.is_absolute() else DATA_ROOT / path
                        for path in (Path(value) for value in frames)
                    )

    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing {len(missing)} frame files; first={missing[0]}")
    if len(paths) != 180_000:
        raise RuntimeError(f"Expected 180000 frame paths, got {len(paths)}")

    stride = max(1, len(paths) // 1000)
    sampled = paths[::stride]
    for path in sampled:
        with Image.open(path) as image:
            if image.size != (256, 256):
                raise RuntimeError(f"Unexpected image size {image.size}: {path}")
            image.verify()

    print(
        f"VALID manifest={MANIFEST} frames={len(paths)} "
        f"sampled_images={len(sampled)} size=256x256"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

