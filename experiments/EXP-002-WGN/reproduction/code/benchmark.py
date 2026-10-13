from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import torch
import yaml


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from wgn import WaveletGuidedNetwork, build_datasets  # noqa: E402
from wgn.data import seed_worker  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs/wgn_ffpp_c23.yaml"))
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--no-pretrained", action="store_true")
    args = parser.parse_args()

    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    torch.manual_seed(config["seed"])
    train_dataset, _, _ = build_datasets(config)
    generator = torch.Generator().manual_seed(config["seed"])
    loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=config["training"]["batch_size"],
        shuffle=True,
        num_workers=config["training"]["workers"],
        pin_memory=True,
        persistent_workers=config["training"]["workers"] > 0,
        prefetch_factor=2 if config["training"]["workers"] > 0 else None,
        drop_last=True,
        worker_init_fn=seed_worker,
        generator=generator,
    )

    model = WaveletGuidedNetwork(
        pretrained=not args.no_pretrained,
        backbone_name=config["model"]["backbone"],
        gate_hidden_dim=config["model"]["gate_hidden_dim"],
    ).cuda().train()
    optimizer = torch.optim.Adam(model.parameters(), lr=config["training"]["learning_rate"])
    loss_fn = torch.nn.BCEWithLogitsLoss()

    measured_steps = min(args.steps, len(loader) - args.warmup)
    if measured_steps <= 0:
        raise ValueError("The loader is too short for the requested warmup")

    torch.cuda.reset_peak_memory_stats()
    started = None
    completed = 0
    for step, batch in enumerate(loader):
        images = batch["image"].cuda(non_blocking=True)
        labels = batch["label"].cuda(non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        logits = model(images)
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()

        if step + 1 == args.warmup:
            torch.cuda.synchronize()
            started = time.perf_counter()
        elif step + 1 > args.warmup:
            completed += 1
            if completed >= measured_steps:
                break

    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    seconds_per_step = elapsed / completed
    samples_per_second = completed * config["training"]["batch_size"] / elapsed
    projected_epoch_seconds = seconds_per_step * len(loader)

    print(f"dataset_samples={len(train_dataset)}")
    print(f"steps_per_epoch={len(loader)}")
    print(f"measured_steps={completed}")
    print(f"elapsed_seconds={elapsed:.3f}")
    print(f"seconds_per_step={seconds_per_step:.4f}")
    print(f"samples_per_second={samples_per_second:.2f}")
    print(f"projected_epoch_minutes={projected_epoch_seconds / 60:.2f}")
    print(f"peak_allocated_gib={torch.cuda.max_memory_allocated() / 1024**3:.3f}")
    print(f"peak_reserved_gib={torch.cuda.max_memory_reserved() / 1024**3:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

