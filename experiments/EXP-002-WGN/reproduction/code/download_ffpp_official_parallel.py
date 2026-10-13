from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DOWNLOADER = ROOT / "faceforensics_download_v4.py"
OUTPUT = Path(r"C:\sp1\data\FaceForensics++-official")
LOG_DIR = ROOT / "runs" / "ffpp_official_download_logs"
DATASETS = (
    "original",
    "Deepfakes",
    "Face2Face",
    "FaceSwap",
    "NeuralTextures",
    "FaceShifter",
)
COMPRESSIONS = ("c23", "c40")


def run_download(task: tuple[str, str]) -> tuple[str, str, int, Path]:
    compression, dataset = task
    log_path = LOG_DIR / f"{compression}_{dataset}.log"
    command = [
        sys.executable,
        str(DOWNLOADER),
        str(OUTPUT),
        "--dataset",
        dataset,
        "--compression",
        compression,
        "--type",
        "videos",
        "--server",
        "EU2",
    ]
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        completed = subprocess.run(
            command,
            input="\n",
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    return compression, dataset, completed.returncode, log_path


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    tasks = [(compression, dataset) for compression in COMPRESSIONS for dataset in DATASETS]
    failures = []
    print(f"START {datetime.now().isoformat()} tasks={len(tasks)} workers=8", flush=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_task = {executor.submit(run_download, task): task for task in tasks}
        for future in as_completed(future_to_task):
            compression, dataset, returncode, log_path = future.result()
            status = "DONE" if returncode == 0 else "FAILED"
            print(
                f"{status} compression={compression} dataset={dataset} "
                f"returncode={returncode} log={log_path}",
                flush=True,
            )
            if returncode != 0:
                failures.append((compression, dataset, log_path))
    print(f"END {datetime.now().isoformat()} failures={len(failures)}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

