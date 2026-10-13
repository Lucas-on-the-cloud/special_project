from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def relative_windows(path: Path, root: Path) -> str:
    return str(PureWindowsPath(*path.relative_to(root).parts))


def collect_group(extracted_root: Path, data_root: Path, label: str) -> dict[str, dict]:
    videos: dict[str, dict] = {}
    for label_dir in sorted(extracted_root.glob(f"*/{label}")):
        shard = label_dir.parent.name
        for sequence_dir in sorted(path for path in label_dir.iterdir() if path.is_dir()):
            frames = sorted(
                path
                for path in sequence_dir.iterdir()
                if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
            )
            if not frames:
                continue
            video_id = f"{shard}/{label}/{sequence_dir.name}"
            videos[video_id] = {
                "label": f"WildDeepfake_{label.capitalize()}",
                "frames": [relative_windows(path, data_root) for path in frames],
            }
    return videos


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="C:/sp1/data")
    parser.add_argument(
        "--extracted-root",
        default="C:/sp1/data/WildDeepfake/extracted",
    )
    parser.add_argument("--output", default="C:/sp1/data/WildDeepfake.json")
    args = parser.parse_args()

    data_root = Path(args.data_root).resolve()
    extracted_root = Path(args.extracted_root).resolve()
    real = collect_group(extracted_root, data_root, "real")
    fake = collect_group(extracted_root, data_root, "fake")
    if not real or not fake:
        raise RuntimeError(f"Expected both real and fake sequences under {extracted_root}")

    payload = {
        "WildDeepfake": {
            "WildDeepfake_Real": {"train": {}, "val": {}, "test": real},
            "WildDeepfake_Fake": {"train": {}, "val": {}, "test": fake},
        }
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(
        json.dumps(
            {
                "output": str(output),
                "real_sequences": len(real),
                "fake_sequences": len(fake),
                "real_frames": sum(len(item["frames"]) for item in real.values()),
                "fake_frames": sum(len(item["frames"]) for item in fake.values()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

