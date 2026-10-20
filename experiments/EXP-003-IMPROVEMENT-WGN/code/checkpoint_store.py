"""Public Hugging Face storage for selected WGN checkpoints."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from urllib.parse import quote

from huggingface_hub import HfApi


REPO_ID = os.environ.get("WGN_CHECKPOINT_REPO", "lucashwang0102/wgn-checkpoints")


def sha256(path: Path) -> str:
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def checkpoint_urls(remote_path: str) -> dict[str, str]:
    encoded = "/".join(quote(part) for part in remote_path.split("/"))
    base = f"https://huggingface.co/{REPO_ID}"
    return {
        "repository": base,
        "browser": f"{base}/blob/main/{encoded}",
        "download": f"{base}/resolve/main/{encoded}",
    }


def _remote_lfs_sha(api: HfApi, remote_path: str) -> str | None:
    info = api.model_info(REPO_ID, files_metadata=True)
    for sibling in info.siblings or []:
        if sibling.rfilename != remote_path:
            continue
        lfs = sibling.lfs
        if isinstance(lfs, dict):
            return lfs.get("sha256")
        return getattr(lfs, "sha256", None)
    raise FileNotFoundError(f"Uploaded checkpoint is absent from {REPO_ID}: {remote_path}")


def ensure_public_repo(api: HfApi) -> None:
    api.create_repo(REPO_ID, repo_type="model", private=False, exist_ok=True)
    info = api.model_info(REPO_ID)
    if info.private:
        raise PermissionError(f"Checkpoint repository must be public: {REPO_ID}")


def upload_checkpoint(local_path: Path, remote_path: str, message: str | None = None) -> dict:
    local_path = Path(local_path)
    if not local_path.is_file():
        raise FileNotFoundError(local_path)
    digest = sha256(local_path)
    api = HfApi()
    ensure_public_repo(api)
    api.upload_file(
        path_or_fileobj=str(local_path),
        path_in_repo=remote_path,
        repo_id=REPO_ID,
        repo_type="model",
        commit_message=message or f"Upload {remote_path}",
    )
    remote_digest = _remote_lfs_sha(api, remote_path)
    if remote_digest and remote_digest != digest:
        raise RuntimeError(
            f"Remote checkpoint hash mismatch for {remote_path}: {remote_digest} != {digest}"
        )
    return {
        "repo_id": REPO_ID,
        "remote_path": remote_path,
        "sha256": digest,
        "bytes": local_path.stat().st_size,
        **checkpoint_urls(remote_path),
    }


def write_checkpoint_pointer(directory: Path, metadata: dict) -> Path:
    """Write the small, versioned pointer that replaces best.pt in Git."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    pointer = {
        "schema_version": 1,
        "storage": "huggingface_public_model_repo",
        **metadata,
    }
    destination = directory / "CHECKPOINT.json"
    destination.write_text(
        json.dumps(pointer, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return destination


def update_registry(registry_path: Path, artifact_path: str, metadata: dict) -> None:
    """Upsert a verified checkpoint record in the repository-wide registry."""
    registry_path = Path(registry_path)
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    else:
        registry = {"schema_version": 1, "checkpoints": []}
    record = {"artifact_path": artifact_path, **metadata}
    records = [item for item in registry["checkpoints"]
               if item.get("artifact_path", item.get("git_path")) != artifact_path]
    records.append(record)
    registry["checkpoints"] = sorted(records, key=lambda item: item["artifact_path"])
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
