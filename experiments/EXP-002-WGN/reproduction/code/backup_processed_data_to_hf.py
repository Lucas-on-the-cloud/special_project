"""Package manifest-referenced processed data into tar shards and upload privately."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import tarfile
import time

from huggingface_hub import HfApi


DATA_ROOT = Path("C:/sp/data")
WORK_ROOT = Path("C:/sp/data-handoff")
STATUS = WORK_ROOT / "upload-status.json"
TZ = timezone(timedelta(hours=7))
DEFAULT_REPO = "lucashwang0102/wgn-private-data"
GROUPS = {
    "ffpp": DATA_ROOT / "FaceForensics++-official.json",
    "celebdf_deepfakebench": DATA_ROOT / "Celeb-DF-v2.json",
    "celebdf_official_direct": DATA_ROOT / "Celeb-DF-v2-official-direct.json",
    "dfdc": DATA_ROOT / "DFDC.json",
    "wilddeepfake": DATA_ROOT / "WildDeepfake.json",
}
METADATA = [
    "FaceForensics++-official.json", "ffpp-filelist.json",
    "Celeb-DF-v2.json", "Celeb-DF-v2.source.json",
    "Celeb-DF-v2-official-direct.json", "DFDC.json", "DFDC.source.json",
    "WildDeepfake.json",
]


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def frame_paths(value) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "frames" and isinstance(child, list):
                found.extend(item for item in child if isinstance(item, str))
            else:
                found.extend(frame_paths(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(frame_paths(child))
    return found


def normalized_records(manifest: Path) -> list[tuple[str, Path, int]]:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    unique = sorted(set(frame_paths(payload)))
    records = []
    missing = []
    root = DATA_ROOT.resolve()
    for raw in unique:
        relative = Path(raw.replace("\\", "/"))
        source = (DATA_ROOT / relative).resolve()
        try:
            source.relative_to(root)
        except ValueError as error:
            raise ValueError(f"Manifest path leaves data root: {raw}") from error
        if not source.is_file():
            missing.append(raw)
            continue
        records.append((relative.as_posix(), source, source.stat().st_size))
    if missing:
        raise FileNotFoundError(f"{manifest.name}: {len(missing)} referenced files missing; first={missing[0]}")
    if not records:
        raise ValueError(f"No frame records found in {manifest}")
    return records


def chunks(records: list[tuple[str, Path, int]], limit: int):
    current, size = [], 0
    for record in records:
        estimated = record[2] + 1024
        if current and size + estimated > limit:
            yield current
            current, size = [], 0
        current.append(record)
        size += estimated
    if current:
        yield current


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def path_digest(records: list[tuple[str, Path, int]]) -> str:
    digest = hashlib.sha256()
    for relative, _, size in records:
        digest.update(f"{relative}\t{size}\n".encode())
    return digest.hexdigest()


def create_shard(path: Path, records: list[tuple[str, Path, int]]) -> None:
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.unlink(missing_ok=True)
    with tarfile.open(temporary, "w", format=tarfile.PAX_FORMAT) as archive:
        for relative, source, _ in records:
            archive.add(source, arcname=relative, recursive=False)
    os.replace(temporary, path)


def upload_file(api: HfApi, repo_id: str, local: Path, remote: str, message: str) -> None:
    api.upload_file(path_or_fileobj=str(local), path_in_repo=remote, repo_id=repo_id,
                    repo_type="dataset", commit_message=message)


def write_support_files(inventory: dict) -> list[Path]:
    metadata_dir = WORK_ROOT / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for name in METADATA:
        source = DATA_ROOT / name
        if source.is_file():
            target = metadata_dir / name
            target.write_bytes(source.read_bytes())
            copied.append(target)
    inventory_path = WORK_ROOT / "DATASET-INVENTORY.json"
    atomic_json(inventory_path, inventory)
    readme = WORK_ROOT / "README.md"
    readme.write_text(
        "# Private WGN processed-data handoff\n\n"
        "Private machine-transfer backup for the WGN experiments. Access is restricted to the "
        "authorized dataset user. The archives contain only files referenced by the locked manifests; "
        "raw videos, source ZIP files, smoke data, and temporary files are excluded.\n\n"
        "Run `restore.ps1` on the destination machine, then run `verify_restored_data.py`.\n",
        encoding="utf-8")
    restore = WORK_ROOT / "restore.ps1"
    restore.write_text(r'''param(
  [string]$RepoId = "lucashwang0102/wgn-private-data",
  [string]$DownloadDir = "C:\sp\data-handoff-download",
  [string]$Destination = "C:\sp\data"
)
$ErrorActionPreference = "Stop"
hf download $RepoId --repo-type dataset --local-dir $DownloadDir
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$expected = @{}
Get-Content (Join-Path $DownloadDir "SHA256SUMS.txt") | ForEach-Object {
  if ($_ -match '^([0-9a-f]{64})\s+(.+)$') { $expected[$matches[2]] = $matches[1] }
}
foreach ($relative in ($expected.Keys | Sort-Object)) {
  $archive = Join-Path $DownloadDir $relative
  $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()
  if ($actual -ne $expected[$relative]) { throw "Checksum mismatch: $relative" }
  tar.exe -xf $archive -C $Destination
  if ($LASTEXITCODE -ne 0) { throw "Extraction failed: $relative" }
}
Copy-Item -Path (Join-Path $DownloadDir "metadata\*") -Destination $Destination -Force
Write-Host "Restore complete. Run verify_restored_data.py." -ForegroundColor Green
''', encoding="utf-8")
    verifier = WORK_ROOT / "verify_restored_data.py"
    verifier.write_text(r'''import json
from pathlib import Path

root = Path("C:/sp/data")
manifests = ["FaceForensics++-official.json", "Celeb-DF-v2.json",
             "Celeb-DF-v2-official-direct.json", "DFDC.json", "WildDeepfake.json"]

def frames(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "frames" and isinstance(child, list):
                yield from (x for x in child if isinstance(x, str))
            else:
                yield from frames(child)
    elif isinstance(value, list):
        for child in value:
            yield from frames(child)

failed = False
for name in manifests:
    values = sorted(set(frames(json.loads((root/name).read_text(encoding="utf-8")))))
    missing = [value for value in values if not (root/Path(value.replace("\\", "/"))).is_file()]
    print(f"{name}: referenced={len(values)} missing={len(missing)}")
    failed |= bool(missing)
raise SystemExit(1 if failed else 0)
''', encoding="utf-8")
    return copied + [inventory_path, readme, restore, verifier]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default=DEFAULT_REPO)
    parser.add_argument("--shard-gib", type=float, default=3.0)
    parser.add_argument("--keep-shards", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    state = read_json(STATUS)
    state.setdefault("schema_version", 1)
    state.setdefault("repo_id", args.repo_id)
    state.setdefault("groups", {})
    state.update(status="planning", pid=os.getpid(), updated_at=now())
    atomic_json(STATUS, state)

    plans = {}
    inventory = {"created_at": now(), "data_root": str(DATA_ROOT), "repo_id": args.repo_id,
                 "selection": "files referenced by locked manifests", "groups": {}}
    total_files = total_bytes = 0
    limit = int(args.shard_gib * 1024 ** 3)
    for group, manifest in GROUPS.items():
        records = normalized_records(manifest)
        group_chunks = list(chunks(records, limit))
        plans[group] = group_chunks
        size = sum(record[2] for record in records)
        inventory["groups"][group] = {"manifest": manifest.name, "files": len(records),
                                      "bytes": size, "path_size_sha256": path_digest(records),
                                      "shards": len(group_chunks)}
        total_files += len(records); total_bytes += size
        print(f"PLAN {group}: files={len(records)} GiB={size/1024**3:.2f} shards={len(group_chunks)}", flush=True)
    inventory.update(total_files=total_files, total_bytes=total_bytes,
                     total_gib=round(total_bytes/1024**3, 3))
    support = write_support_files(inventory)
    state.update(status="planned", inventory=inventory, updated_at=now())
    atomic_json(STATUS, state)
    if args.plan_only:
        return

    api = HfApi()
    repo = api.repo_info(args.repo_id, repo_type="dataset")
    if not repo.private:
        raise PermissionError(f"Refusing to upload processed data to non-private repo: {args.repo_id}")
    sums = []
    for group, group_chunks in plans.items():
        group_state = state["groups"].setdefault(group, {})
        for index, records in enumerate(group_chunks):
            name = f"shards/{group}/{group}-{index:03d}.tar"
            existing = group_state.get(str(index), {})
            if existing.get("status") == "uploaded":
                sums.append((existing["sha256"], name))
                print(f"SKIP_UPLOADED {name}", flush=True)
                continue
            local = WORK_ROOT / Path(name).name
            reusable = (
                existing.get("status") == "packed"
                and local.is_file()
                and local.stat().st_size == existing.get("bytes")
                and existing.get("files") == len(records)
            )
            if reusable and sha256(local) == existing.get("sha256"):
                digest = existing["sha256"]
                print(f"REUSE_PACKED {name} sha256={digest}", flush=True)
            else:
                state.update(status="packing", current=name, updated_at=now())
                atomic_json(STATUS, state)
                create_shard(local, records)
                digest = sha256(local)
                group_state[str(index)] = {"status": "packed", "sha256": digest,
                                           "bytes": local.stat().st_size, "files": len(records)}
                atomic_json(STATUS, state)
            state.update(status="uploading", current=name, updated_at=now())
            atomic_json(STATUS, state)
            upload_file(api, args.repo_id, local, name, f"Upload {group} shard {index:03d}")
            group_state[str(index)].update(status="uploaded", uploaded_at=now())
            sums.append((digest, name))
            atomic_json(STATUS, state)
            print(f"UPLOADED {name} sha256={digest}", flush=True)
            if not args.keep_shards:
                local.unlink(missing_ok=True)

    checksum = WORK_ROOT / "SHA256SUMS.txt"
    checksum.write_text("".join(f"{digest}  {name}\n" for digest, name in sums), encoding="utf-8")
    for local in support + [checksum]:
        relative = local.relative_to(WORK_ROOT).as_posix()
        upload_file(api, args.repo_id, local, relative, f"Update handoff metadata: {relative}")
    remote_files = set(api.list_repo_files(args.repo_id, repo_type="dataset"))
    expected = {name for _, name in sums} | {path.relative_to(WORK_ROOT).as_posix() for path in support + [checksum]}
    missing = sorted(expected - remote_files)
    if missing:
        raise RuntimeError(f"Remote verification missing {len(missing)} files: {missing[:3]}")
    state.update(status="complete", current=None, completed_at=now(), remote_files=len(remote_files))
    atomic_json(STATUS, state)
    print(f"BACKUP_COMPLETE repo={args.repo_id} files={total_files} GiB={total_bytes/1024**3:.2f}", flush=True)


if __name__ == "__main__":
    main()

