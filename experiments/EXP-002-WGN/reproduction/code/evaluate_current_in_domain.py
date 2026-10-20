"""Evaluate one independently trained current-machine WGN checkpoint in-domain."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import torch


CODE = Path(__file__).resolve().parent
REPO = CODE.parents[3]
EXP3_CODE = REPO / "experiments" / "EXP-003-IMPROVEMENT-WGN" / "code"
sys.path.insert(0, str(EXP3_CODE))

from common import atomic_json, config_load, make_model, sha256  # noqa: E402
from data import build_datasets  # noqa: E402
from preflight import inspect  # noqa: E402
from train import evaluate, loader  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    run = Path(args.run)
    config = config_load(args.config)
    if not (run / "summary.json").is_file():
        raise FileNotFoundError("Final training must finish before in-domain evaluation")
    checkpoint = run / "best.pt"
    _, _, test = build_datasets(config)
    inspect(test, args.label, full_decode=False)
    identity = hashlib.sha256(json.dumps([
        (str(record.path), record.label, record.manipulation, record.video)
        for record in test.records
    ]).encode()).hexdigest()
    model = make_model(config, pretrained=False).cuda().eval()
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model.load_state_dict(payload["model"], strict=True)
    measured = evaluate(model, loader(test, config))
    result = {
        "dataset": args.label,
        "checkpoint_sha256": sha256(checkpoint),
        "manifest_sha256": identity,
        "checkpoint_epoch_zero_based": payload["epoch"],
        "metrics": measured,
    }
    atomic_json(run / "in_domain_evaluation.json", result)
    print(json.dumps(result, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()

