from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score
import torch
from torch.utils.data import DataLoader
import yaml


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from wgn.data import FaceForensicsJsonDataset, build_records  # noqa: E402
from wgn.model import WaveletGuidedNetwork  # noqa: E402


GROUPS = ("FF-DF", "FF-F2F", "FF-FS", "FF-NT")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--config", default=str(ROOT / "configs/wgn_ffpp_c23.yaml"))
    args = parser.parse_args()

    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    model = WaveletGuidedNetwork(
        pretrained=False,
        backbone_name=config["model"]["backbone"],
        gate_hidden_dim=config["model"]["gate_hidden_dim"],
    ).cuda().eval()
    checkpoint = torch.load(args.checkpoint, map_location="cuda", weights_only=False)
    model.load_state_dict(checkpoint["model"])

    results = {}
    for group in GROUPS:
        records = build_records(
            json_path=Path(config["data"]["json"]),
            data_root=Path(config["data"]["root"]),
            split="test",
            frames_per_real=config["data"]["frames_per_real"],
            frames_per_fake=config["data"]["frames_per_fake"],
            manipulations=(group,),
            compression=str(config["data"].get("compression", "c23")),
        )
        dataset = FaceForensicsJsonDataset(records, train=False)
        loader = DataLoader(
            dataset,
            batch_size=config["training"]["batch_size"],
            shuffle=False,
            num_workers=config["training"]["workers"],
            pin_memory=True,
            persistent_workers=config["training"]["workers"] > 0,
        )
        labels = []
        scores = []
        with torch.no_grad():
            for batch in loader:
                logits = model(batch["image"].cuda(non_blocking=True))
                labels.append(batch["label"])
                scores.append(torch.sigmoid(logits).cpu())
        y_true = torch.cat(labels).numpy()
        y_score = torch.cat(scores).numpy()
        results[group] = {
            "frames": len(dataset),
            "accuracy": float(accuracy_score(y_true, y_score >= 0.5)),
            "auc": float(roc_auc_score(y_true, y_score)),
        }

    results["average_auc"] = float(np.mean([results[group]["auc"] for group in GROUPS]))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, sort_keys=True)
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

