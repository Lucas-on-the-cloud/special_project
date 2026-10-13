from __future__ import annotations

import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PREPROCESSOR = ROOT / "preprocess_ffpp_official.py"
OUTPUT_ROOT = Path(r"C:\sp1\data\FaceForensics++-official-processed")
DATA_ROOT = Path(r"C:\sp1\data")
PARTIAL_ROOT = DATA_ROOT / "ffpp_official_manifests"
FINAL_MANIFEST = DATA_ROOT / "FaceForensics++-official.json"
LOG_ROOT = ROOT / "runs" / "ffpp_official_preprocess_logs"
GROUPS = ("FF-real", "FF-DF", "FF-F2F", "FF-FS", "FF-NT", "FF-FSh")
COMPRESSIONS = ("c23", "c40")
SPLITS = ("train", "val", "test")


def run_task(task: tuple[str, str]) -> tuple[str, str, int, Path, Path]:
    compression, group = task
    safe_group = group.replace("-", "_")
    manifest = PARTIAL_ROOT / f"{compression}_{safe_group}.json"
    log_path = LOG_ROOT / f"{compression}_{safe_group}.log"
    command = [
        sys.executable,
        str(PREPROCESSOR),
        "--compressions",
        compression,
        "--groups",
        group,
        "--output-root",
        str(OUTPUT_ROOT),
        "--manifest",
        str(manifest),
        "--detector-size",
        "512",
        "--batch-size",
        "16",
    ]
    environment = os.environ.copy()
    environment["TORCH_HOME"] = r"C:\sp1\.cache\torch"
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        completed = subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=environment,
            check=False,
        )
    return compression, group, completed.returncode, log_path, manifest


def merge_manifests(manifests: list[Path]) -> None:
    merged = {
        "FaceForensics++": {
            group: {
                split: {compression: {} for compression in COMPRESSIONS}
                for split in SPLITS
            }
            for group in GROUPS
        }
    }
    for path in manifests:
        with path.open("r", encoding="utf-8") as handle:
            partial = json.load(handle)["FaceForensics++"]
        for group, split_data in partial.items():
            for split, compression_data in split_data.items():
                for compression, videos in compression_data.items():
                    merged["FaceForensics++"][group][split][compression].update(videos)

    expected_videos = {"train": 720, "val": 140, "test": 140}
    for group in GROUPS:
        expected_frames = 40 if group == "FF-real" else 10
        for compression in COMPRESSIONS:
            for split in SPLITS:
                videos = merged["FaceForensics++"][group][split][compression]
                if len(videos) != expected_videos[split]:
                    raise RuntimeError(
                        f"Invalid video count {group}/{compression}/{split}: {len(videos)}"
                    )
                bad = [name for name, item in videos.items() if len(item["frames"]) != expected_frames]
                if bad:
                    raise RuntimeError(
                        f"Invalid frame count {group}/{compression}/{split}: {bad[:5]}"
                    )
    with FINAL_MANIFEST.open("w", encoding="utf-8") as handle:
        json.dump(merged, handle, indent=2)


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    PARTIAL_ROOT.mkdir(parents=True, exist_ok=True)
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    tasks = [(compression, group) for compression in COMPRESSIONS for group in GROUPS]
    manifests: list[Path] = []
    failures = []
    print(f"START {datetime.now().isoformat()} tasks={len(tasks)} workers=4", flush=True)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(run_task, task): task for task in tasks}
        for future in as_completed(futures):
            compression, group, returncode, log_path, manifest = future.result()
            status = "DONE" if returncode == 0 else "FAILED"
            print(
                f"{status} compression={compression} group={group} "
                f"returncode={returncode} log={log_path}",
                flush=True,
            )
            if returncode == 0:
                manifests.append(manifest)
            else:
                failures.append((compression, group, log_path))
    if failures:
        print(f"END {datetime.now().isoformat()} failures={len(failures)}", flush=True)
        return 1
    merge_manifests(manifests)
    print(f"WROTE_MANIFEST {FINAL_MANIFEST}", flush=True)
    print(f"END {datetime.now().isoformat()} failures=0", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

