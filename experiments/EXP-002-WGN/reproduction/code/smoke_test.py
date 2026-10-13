from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch
import yaml


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from wgn import WaveletGuidedNetwork, build_datasets  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(ROOT / "configs/wgn_ffpp_c23.yaml"))
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--pretrained", action="store_true")
    args = parser.parse_args()

    with Path(args.config).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    train_dataset, val_dataset, test_dataset = build_datasets(config)
    model = WaveletGuidedNetwork(
        pretrained=args.pretrained,
        backbone_name=config["model"]["backbone"],
        gate_hidden_dim=config["model"]["gate_hidden_dim"],
    ).cuda().train()

    loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
        drop_last=True,
    )
    batch = next(iter(loader))
    images = batch["image"].cuda()
    labels = batch["label"].cuda()

    torch.cuda.reset_peak_memory_stats()
    logits = model(images)
    loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, labels)
    loss.backward()
    torch.cuda.synchronize()

    total = sum(parameter.numel() for parameter in model.parameters())
    trainable = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    print(f"train_samples={len(train_dataset)}")
    print(f"val_samples={len(val_dataset)}")
    print(f"test_samples={len(test_dataset)}")
    print(f"parameters_total={total}")
    print(f"parameters_trainable={trainable}")
    print(f"input_shape={tuple(images.shape)}")
    print(f"logit_shape={tuple(logits.shape)}")
    print(f"loss={loss.item():.8f}")
    print(f"peak_allocated_gib={torch.cuda.max_memory_allocated() / 1024**3:.3f}")
    print(f"peak_reserved_gib={torch.cuda.max_memory_reserved() / 1024**3:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

