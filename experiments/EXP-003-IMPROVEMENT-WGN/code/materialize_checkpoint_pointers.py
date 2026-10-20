"""Replace Git checkpoint artifacts with verified Hugging Face pointers."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from checkpoint_store import write_checkpoint_pointer


ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "docs" / "checkpoint-registry.json"


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for entry in registry["checkpoints"]:
        artifact_path = entry.get("artifact_path", entry.get("git_path"))
        checkpoint = ROOT / artifact_path
        if checkpoint.exists() and sha256(checkpoint) != entry["sha256"]:
            raise RuntimeError(f"Local checkpoint hash mismatch: {checkpoint}")
        directory = checkpoint.parent
        metadata = {key: value for key, value in entry.items()
                    if key not in {"artifact_path", "git_path"}}
        write_checkpoint_pointer(directory, metadata)

        readme_path = directory / "README.md"
        if readme_path.exists():
            readme = readme_path.read_text(encoding="utf-8")
            readme = re.sub(
                r"Use `best\.pt`.*?resumed\.\n\n",
                "The selected `best.pt` is stored in the private Hugging Face model "
                f"repository. Download it from [Hugging Face]({entry['browser']}) after "
                "authentication, then verify the SHA-256 above. `CHECKPOINT.json` records "
                "the stable remote path and download URL. `last.pt` remains local unless "
                "an unfinished run must be moved.\n\n",
                readme,
                flags=re.DOTALL,
            )
            readme_path.write_text(readme, encoding="utf-8")

        manifest_path = directory / "ARTIFACT-MANIFEST.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest.update({
                "schema_version": 2,
                "checkpoint_sha256": entry["sha256"],
                "checkpoint_bytes": entry["bytes"],
                "checkpoint_hf_repo": entry["repo_id"],
                "checkpoint_hf_path": entry["remote_path"],
                "checkpoint_url": entry["browser"],
            })
        excluded = {"best.pt", "SHA256SUMS.txt", "ARTIFACT-MANIFEST.json"}
        files = sorted(path for path in directory.iterdir()
                       if path.is_file() and path.name not in excluded)
        (directory / "SHA256SUMS.txt").write_text(
            "".join(f"{sha256(path)}  {path.name}\n" for path in files), encoding="utf-8"
        )
        if manifest_path.exists():
            inventoried = sorted(path for path in directory.iterdir()
                                 if path.is_file() and path.name not in {"best.pt", "ARTIFACT-MANIFEST.json"})
            manifest["files"] = [
                {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in inventoried
            ]
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )

    print(json.dumps({"status": "complete", "pointers": len(registry["checkpoints"])}))


if __name__ == "__main__":
    main()
