from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score
import torch
from torch.utils.data import DataLoader
import yaml


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from wgn.data import FaceForensicsJsonDataset, build_binary_dataset_records  # noqa: E402
from wgn.model import WaveletGuidedNetwork  # noqa: E402


def metrics(labels, scores):
    return {
        "accuracy": float(accuracy_score(labels, np.asarray(scores) >= 0.5)),
        "auc": float(roc_auc_score(labels, scores)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs/wgn_ffpp_c23.yaml"))
    parser.add_argument("--checkpoint", default=str(ROOT / "runs/wgn_ffpp_c23/best.pt"))
    parser.add_argument("--json", default="C:/sp1/data/Celeb-DF-v2.json")
    parser.add_argument("--data-root", default="C:/sp1/data")
    parser.add_argument("--dataset", default="Celeb-DF-v2")
    parser.add_argument("--real-group", default="CelebDFv2_real")
    parser.add_argument("--fake-group", default="CelebDFv2_fake")
    parser.add_argument("--split", default="test")
    parser.add_argument("--frames-per-video", type=int, default=0)
    parser.add_argument("--output", default=str(ROOT / "runs/wgn_ffpp_c23/cross_celeb_df_v2.json"))
    args = parser.parse_args()

    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    records = build_binary_dataset_records(
        json_path=Path(args.json),
        data_root=Path(args.data_root),
        dataset_name=args.dataset,
        real_group=args.real_group,
        fake_group=args.fake_group,
        split=args.split,
        frames_per_video=args.frames_per_video,
    )
    dataset = FaceForensicsJsonDataset(records, train=False, image_size=256)
    loader = DataLoader(
        dataset,
        batch_size=config["training"]["batch_size"],
        shuffle=False,
        num_workers=config["training"]["workers"],
        pin_memory=True,
        persistent_workers=config["training"]["workers"] > 0,
    )

    model = WaveletGuidedNetwork(
        pretrained=False,
        backbone_name=config["model"]["backbone"],
        gate_hidden_dim=config["model"]["gate_hidden_dim"],
    ).cuda().eval()
    checkpoint = torch.load(args.checkpoint, map_location="cuda", weights_only=False)
    model.load_state_dict(checkpoint["model"])

    label_parts = []
    score_parts = []
    keys: list[str] = []
    with torch.no_grad():
        for batch in loader:
            logits = model(batch["image"].cuda(non_blocking=True))
            label_parts.append(batch["label"])
            score_parts.append(torch.sigmoid(logits).cpu())
            keys.extend(
                f"{group}/{video}" for group, video in zip(batch["manipulation"], batch["video"])
            )

    labels = torch.cat(label_parts).numpy()
    scores = torch.cat(score_parts).numpy()
    video_scores: dict[str, list[float]] = defaultdict(list)
    video_labels: dict[str, int] = {}
    for key, label, score in zip(keys, labels, scores):
        video_scores[key].append(float(score))
        video_labels[key] = int(label)
    ordered = sorted(video_scores)
    result = {
        "dataset": args.dataset,
        "split": args.split,
        "frames": len(dataset),
        "videos": len(ordered),
        "frame": metrics(labels, scores),
        "video": metrics(
            [video_labels[key] for key in ordered],
            [float(np.mean(video_scores[key])) for key in ordered],
        ),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

