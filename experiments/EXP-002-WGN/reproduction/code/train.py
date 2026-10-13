from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score
import torch
import yaml


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from wgn import WaveletGuidedNetwork, build_datasets  # noqa: E402
from wgn.data import seed_worker  # noqa: E402


def make_loader(dataset, config: dict, train: bool):
    workers = int(config["training"]["workers"])
    generator = torch.Generator().manual_seed(config["seed"])
    return torch.utils.data.DataLoader(
        dataset,
        batch_size=int(config["training"]["batch_size"]),
        shuffle=train,
        num_workers=workers,
        pin_memory=True,
        persistent_workers=workers > 0,
        prefetch_factor=2 if workers > 0 else None,
        drop_last=train,
        worker_init_fn=seed_worker,
        generator=generator,
    )


def compute_metrics(labels: list[float], probabilities: list[float]) -> dict[str, float]:
    predicted = [int(value >= 0.5) for value in probabilities]
    return {
        "accuracy": float(accuracy_score(labels, predicted)),
        "auc": float(roc_auc_score(labels, probabilities)),
    }


@torch.no_grad()
def evaluate(model, loader, loss_fn) -> dict[str, float]:
    model.eval()
    losses: list[torch.Tensor] = []
    label_tensors: list[torch.Tensor] = []
    probability_tensors: list[torch.Tensor] = []
    video_keys: list[str] = []
    video_scores: dict[str, list[float]] = defaultdict(list)
    video_labels: dict[str, int] = {}

    for batch in loader:
        images = batch["image"].cuda(non_blocking=True)
        targets = batch["label"].cuda(non_blocking=True)
        logits = model(images)
        losses.append(loss_fn(logits, targets).detach())
        label_tensors.append(targets.detach())
        probability_tensors.append(torch.sigmoid(logits.detach()))
        video_keys.extend(
            f"{group}/{video}" for group, video in zip(batch["manipulation"], batch["video"])
        )

    labels = torch.cat(label_tensors).cpu().tolist()
    probabilities = torch.cat(probability_tensors).cpu().tolist()
    for key, label, score in zip(video_keys, labels, probabilities):
        video_scores[key].append(score)
        video_labels[key] = int(label)

    result = {
        "loss": float(torch.stack(losses).mean().item()),
        **compute_metrics(labels, probabilities),
    }
    ordered_keys = sorted(video_scores)
    result.update(
        {
            f"video_{name}": value
            for name, value in compute_metrics(
                [video_labels[key] for key in ordered_keys],
                [float(np.mean(video_scores[key])) for key in ordered_keys],
            ).items()
        }
    )
    return result


def train_epoch(model, loader, optimizer, loss_fn, max_steps: int | None = None) -> dict[str, float]:
    model.train()
    losses: list[torch.Tensor] = []
    label_tensors: list[torch.Tensor] = []
    probability_tensors: list[torch.Tensor] = []
    started = time.perf_counter()
    for step, batch in enumerate(loader):
        images = batch["image"].cuda(non_blocking=True)
        targets = batch["label"].cuda(non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = loss_fn(logits, targets)
        loss.backward()
        optimizer.step()
        losses.append(loss.detach())
        label_tensors.append(targets.detach())
        probability_tensors.append(torch.sigmoid(logits.detach()))
        if max_steps is not None and step + 1 >= max_steps:
            break
    torch.cuda.synchronize()
    labels = torch.cat(label_tensors).cpu().tolist()
    probabilities = torch.cat(probability_tensors).cpu().tolist()
    return {
        "loss": float(torch.stack(losses).mean().item()),
        **compute_metrics(labels, probabilities),
        "seconds": time.perf_counter() - started,
        "steps": len(losses),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs/wgn_ffpp_c23.yaml"))
    parser.add_argument("--epochs", type=int)
    parser.add_argument("--max-train-steps", type=int)
    parser.add_argument("--no-pretrained", action="store_true")
    parser.add_argument("--manipulations", nargs="+", choices=["FF-DF", "FF-F2F", "FF-FS", "FF-NT"])
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if args.epochs is not None:
        config["training"]["epochs"] = args.epochs
    if args.manipulations is not None:
        config["data"]["manipulations"] = args.manipulations
    if args.output_dir is not None:
        config["training"]["output_dir"] = args.output_dir

    seed = int(config["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    output_dir = Path(config["training"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "resolved_config.yaml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=False)

    train_dataset, val_dataset, test_dataset = build_datasets(config)
    train_loader = make_loader(train_dataset, config, train=True)
    val_loader = make_loader(val_dataset, config, train=False)
    test_loader = make_loader(test_dataset, config, train=False)

    model = WaveletGuidedNetwork(
        pretrained=bool(config["model"]["pretrained"]) and not args.no_pretrained,
        backbone_name=config["model"]["backbone"],
        gate_hidden_dim=int(config["model"]["gate_hidden_dim"]),
    ).cuda()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=float(config["training"]["learning_rate"]),
        weight_decay=float(config["training"]["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=int(config["training"]["epochs"])
    )
    loss_fn = torch.nn.BCEWithLogitsLoss()

    best_accuracy = -1.0
    history_path = output_dir / "metrics.jsonl"
    for epoch in range(int(config["training"]["epochs"])):
        train_metrics = train_epoch(
            model, train_loader, optimizer, loss_fn, max_steps=args.max_train_steps
        )
        val_metrics = evaluate(model, val_loader, loss_fn)
        scheduler.step()
        record = {
            "epoch": epoch,
            "lr": optimizer.param_groups[0]["lr"],
            "train": train_metrics,
            "val": val_metrics,
        }
        print(json.dumps(record, sort_keys=True), flush=True)
        with history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        if val_metrics["accuracy"] > best_accuracy:
            best_accuracy = val_metrics["accuracy"]
            torch.save(
                {"epoch": epoch, "model": model.state_dict(), "config": config, "val": val_metrics},
                output_dir / "best.pt",
            )

    checkpoint = torch.load(output_dir / "best.pt", map_location="cuda", weights_only=False)
    model.load_state_dict(checkpoint["model"])
    test_metrics = evaluate(model, test_loader, loss_fn)
    summary = {"best_epoch": checkpoint["epoch"], "best_val": checkpoint["val"], "test": test_metrics}
    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
    print(json.dumps(summary, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

