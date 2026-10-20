"""Upload selected WGN best checkpoints to the private model repository."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from checkpoint_store import REPO_ID, upload_checkpoint, write_checkpoint_pointer


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "docs" / "checkpoint-registry.json"
TZ = timezone(timedelta(hours=7))


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def write_registry(entries: list[dict]) -> None:
    payload = {
        "schema_version": 1,
        "updated_at": now(),
        "repo_id": REPO_ID,
        "private": True,
        "checkpoints": sorted(entries, key=lambda value: value["artifact_path"]),
    }
    REGISTRY.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", action="append", type=Path)
    args = parser.parse_args()
    checkpoints = args.checkpoint or sorted((ROOT / "experiments").glob("**/artifacts/**/best.pt"))
    if not checkpoints:
        raise FileNotFoundError("No selected best.pt checkpoints found")
    entries = []
    for path in checkpoints:
        path = path.resolve()
        relative = path.relative_to(ROOT).as_posix()
        uploaded = upload_checkpoint(path, relative, f"Back up {relative}")
        entry = {"artifact_path": relative, **uploaded, "uploaded_at": now()}
        entries.append(entry)
        write_checkpoint_pointer(path.parent, uploaded | {"uploaded_at": entry["uploaded_at"]})
        write_registry(entries)
        print(json.dumps({"event": "uploaded", **entry}), flush=True)
    print(json.dumps({"status": "complete", "repo_id": REPO_ID, "files": len(entries)}), flush=True)


if __name__ == "__main__":
    main()
