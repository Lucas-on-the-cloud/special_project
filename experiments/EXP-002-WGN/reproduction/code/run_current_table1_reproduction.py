"""Finish paper Table 1 on the RTX 5060 Ti and publish all three comparisons."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timedelta, timezone
import hashlib
import json
import msvcrt
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


CODE = Path(__file__).resolve().parent
REPRODUCTION = CODE.parent
REPO = CODE.parents[3]
EXP3_CODE = REPO / "experiments" / "EXP-003-IMPROVEMENT-WGN" / "code"
CONFIGS = CODE / "configs" / "current-rtx5060-table1"
RUNS = Path("C:/sp/runs/wgn_reproduction_table1")
CROSS_RUNS = Path("C:/sp/runs/wgn_reproduction_current")
ARTIFACTS = REPRODUCTION / "artifacts" / "current-table1"
REPORT = REPRODUCTION / "CURRENT-FULL-REPRODUCTION.md"
BASELINE = REPRODUCTION / "artifacts" / "baseline_final"
CROSS_COMPARISON = REPRODUCTION / "evidence" / "current-cross-manipulation" / "comparison.json"
GIT = Path("C:/sp/.tools/git-portable/cmd/git.exe")
TZ = timezone(timedelta(hours=7))
STILL_ACTIVE = 259
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

RUN_SPECS = {
    "ffpp_c40": ("FF++ c40", CONFIGS / "ffpp_c40.yaml"),
    "faceshifter_c23": ("FaceShifter c23", CONFIGS / "faceshifter_c23.yaml"),
    "faceshifter_c40": ("FaceShifter c40", CONFIGS / "faceshifter_c40.yaml"),
}

PAPER_TABLE1 = {
    "FF++ c23": (95.32, 98.90), "FF++ c40": (80.20, 89.00),
    "FaceShifter c23": (98.00, 99.92), "FaceShifter c40": (94.99, 98.66),
}
RTX5090_TABLE1 = {
    "FF++ c23": (94.12, 98.44), "FF++ c40": (78.80, 87.09),
    "FaceShifter c23": (98.24, 98.88), "FaceShifter c40": (93.87, 97.20),
}
PAPER_TABLE2 = {"Celeb-DF v2": 77.62, "DFDC": 70.41, "WildDeepfake": 68.65}
RTX5090_TABLE2 = {
    "Celeb-DF v2": (65.03, 69.70), "DFDC": (69.54, 71.00),
    "WildDeepfake": (70.35, 75.35),
}


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for attempt in range(30):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(min(.01 * (attempt + 1), .25))


def process_alive(pid) -> bool:
    if not isinstance(pid, int) or pid <= 0:
        return False
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return False
    try:
        code = ctypes.c_ulong()
        return bool(ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))) and code.value == STILL_ACTIVE
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


class Runner:
    def __init__(self, interval: int, no_publish: bool):
        RUNS.mkdir(parents=True, exist_ok=True)
        (RUNS / "logs").mkdir(exist_ok=True)
        self.interval, self.no_publish = interval, no_publish
        self.lock = (RUNS / "runner.lock").open("a+b")
        self.lock.seek(0)
        if not self.lock.read(1):
            self.lock.write(b"0")
            self.lock.flush()
        self.lock.seek(0)
        msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        self.status_path = RUNS / "status.json"
        self.state = read_json(self.status_path)
        self.state.setdefault("stages", {})
        self.state.pop("error", None)
        self.state["pid"] = os.getpid()
        (RUNS / "runner.pid").write_text(str(os.getpid()), encoding="ascii")
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

    def close(self) -> None:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        self.lock.close()

    def update(self, phase: str, **values) -> None:
        if phase != "failed":
            self.state.pop("error", None)
        self.state.update(updated_at=now(), phase=phase, **values)
        atomic_json(self.status_path, self.state)

    def event(self, message: str) -> None:
        line = f"{now()} {message}"
        print(line, flush=True)
        with (RUNS / "events.log").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def wait_for_table3(self) -> None:
        previous = None
        while True:
            cross = read_json(CROSS_RUNS / "status.json")
            phase, pid = cross.get("phase", "unavailable"), cross.get("pid")
            if phase == "complete" and not process_alive(pid):
                self.event("TABLE3_COMPLETE; STARTING_TABLE1_REMAINDER")
                return
            if phase != previous:
                self.event(f"WAIT_TABLE3 phase={phase} pid={pid}")
                previous = phase
            self.update("waiting_for_table3", table3_phase=phase, table3_pid=pid)
            time.sleep(self.interval)

    def command(self, stage: str, arguments: list[object], cwd: Path = EXP3_CODE) -> None:
        if self.state["stages"].get(stage, {}).get("status") == "complete":
            self.event(f"SKIP_COMPLETE {stage}")
            return
        log = RUNS / "logs" / f"{stage}.log"
        environment = os.environ.copy()
        environment.update(TORCH_HOME="C:/sp/.cache/torch", HF_HOME="C:/sp/.cache/huggingface",
                           PYTHONUNBUFFERED="1", GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
        for attempt in range(1, 3):
            self.state["stages"][stage] = {"status": "running", "attempt": attempt,
                                                   "started_at": now(), "log": str(log)}
            self.update(stage)
            self.event(f"START {stage} attempt={attempt}")
            with log.open("a", encoding="utf-8") as handle:
                handle.write("\nCOMMAND " + json.dumps([str(value) for value in arguments]) + "\n")
                handle.flush()
                process = subprocess.Popen([str(value) for value in arguments], cwd=cwd, env=environment,
                                           stdout=handle, stderr=subprocess.STDOUT)
                self.state["stages"][stage]["child_pid"] = process.pid
                while process.poll() is None:
                    self.update(stage)
                    time.sleep(10)
            status = "complete" if process.returncode == 0 else "failed"
            self.state["stages"][stage].update(status=status, returncode=process.returncode, ended_at=now())
            self.update(stage)
            self.event(f"{status.upper()} {stage} exit={process.returncode}")
            if process.returncode == 0:
                return
        raise RuntimeError(f"{stage} failed twice; inspect {log}")

    def execute(self) -> None:
        self.wait_for_table3()
        for slug, (label, config) in RUN_SPECS.items():
            run = RUNS / f"{slug}_final"
            self.command(f"smoke_{slug}", [sys.executable, EXP3_CODE / "smoke_test.py",
                         "--config", config, "--output", RUNS / "smoke" / f"{slug}.json"])
            self.command(f"train_{slug}", [sys.executable, EXP3_CODE / "train.py", "--config", config,
                         "--output-dir", run, "--resume"])
            self.command(f"evaluate_{slug}", [sys.executable, CODE / "evaluate_current_in_domain.py",
                         "--config", config, "--run", run, "--label", label], cwd=CODE)
        self.publish()
        self.update("complete")
        self.event("CURRENT_WGN_FULL_REPRODUCTION_COMPLETE")

    def publish(self) -> None:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        for slug in RUN_SPECS:
            run, target = RUNS / f"{slug}_final", ARTIFACTS / slug
            required = ("best.pt", "summary.json", "in_domain_evaluation.json")
            if not all((run / name).is_file() for name in required):
                raise FileNotFoundError(f"Incomplete Table 1 run: {slug}")
            target.mkdir(parents=True, exist_ok=True)
            for name in ("best.pt", "summary.json", "resolved_config.yaml", "environment.json",
                         "metrics.jsonl", "progress.json", "in_domain_evaluation.json", "source.patch"):
                if (run / name).exists():
                    shutil.copy2(run / name, target / name)
            training_log = RUNS / "logs" / f"train_{slug}.log"
            evaluation_log = RUNS / "logs" / f"evaluate_{slug}.log"
            shutil.copy2(training_log, target / "training.log")
            shutil.copy2(evaluation_log, target / "evaluation.log")
            (target / "SHA256SUMS.txt").write_text(f"{sha256(run / 'best.pt')}  best.pt\n", encoding="utf-8")
        comparison = build_comparison()
        atomic_json(REPRODUCTION / "CURRENT-FULL-REPRODUCTION.json", comparison)
        REPORT.write_text(render_report(comparison), encoding="utf-8")
        update_status(comparison)
        if self.no_publish:
            self.event("PUBLICATION_SKIPPED_BY_ARGUMENT")
        else:
            publish_git()


def metric(path: Path) -> dict:
    return read_json(path)["metrics"]


def build_comparison() -> dict:
    baseline = read_json(BASELINE / "evaluation.json")["datasets"]
    current_table1 = {
        "FF++ c23": baseline["FF++ c23"],
        **{label: metric(RUNS / f"{slug}_final" / "in_domain_evaluation.json")
           for slug, (label, _) in RUN_SPECS.items()},
    }
    aliases = {"Celeb-DF v2": "Celeb-DF-v2", "DFDC": "DFDC", "WildDeepfake": "WildDeepfake"}
    table2 = {name: baseline[key] for name, key in aliases.items()}
    return {
        "completed_at": now(), "machine": "NVIDIA RTX 5060 Ti 16 GB",
        "protocol": "paper-aligned independent training; 25 epochs; validation-accuracy checkpoint selection",
        "table1": {name: {
            "paper": {"accuracy": PAPER_TABLE1[name][0], "auc": PAPER_TABLE1[name][1]},
            "rtx5090_historical": {"accuracy": RTX5090_TABLE1[name][0], "auc": RTX5090_TABLE1[name][1]},
            "rtx5060ti_current": {"accuracy": 100 * current_table1[name]["accuracy"],
                                  "auc": 100 * current_table1[name]["auc"],
                                  "video_accuracy": 100 * current_table1[name]["video_accuracy"],
                                  "video_auc": 100 * current_table1[name]["video_auc"]},
        } for name in PAPER_TABLE1},
        "table2": {name: {
            "paper_auc": PAPER_TABLE2[name],
            "rtx5090_historical": {"frame_auc": RTX5090_TABLE2[name][0], "video_auc": RTX5090_TABLE2[name][1]},
            "rtx5060ti_current": {"frame_auc": 100 * table2[name]["auc"],
                                  "video_auc": 100 * table2[name]["video_auc"],
                                  "frames": table2[name]["frames"], "videos": table2[name]["videos"]},
        } for name in PAPER_TABLE2},
        "celebdf_official_direct_diagnostic": baseline["Celeb-DF-v2 official-direct"],
        "table3": read_json(CROSS_COMPARISON),
    }


def render_matrix(title: str, key: str, table3: dict) -> list[str]:
    lines = [f"### {title}", "", "| Train / Test | DF | F2F | FS | NT | Avg |",
             "|---|---:|---:|---:|---:|---:|"]
    for name in ("DF", "F2F", "FS", "NT"):
        values = table3["rows"][name][key]
        lines.append("| " + name + " | " + " | ".join(f"{value:.2f}" for value in values) + " |")
    return lines + [""]


def render_report(result: dict) -> str:
    lines = ["# Current RTX 5060 Ti WGN reproduction", "",
             "This report follows the three evaluation tables used by the archived RTX 5090 reproduction.", "",
             "## Table 1 — independently trained in-domain models", "",
             "| Experiment | Paper ACC | Paper AUC | RTX 5090 ACC | RTX 5090 AUC | RTX 5060 Ti ACC | RTX 5060 Ti AUC | Δ AUC vs paper |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, row in result["table1"].items():
        paper, old, new = row["paper"], row["rtx5090_historical"], row["rtx5060ti_current"]
        lines.append(f"| {name} | {paper['accuracy']:.2f} | {paper['auc']:.2f} | {old['accuracy']:.2f} | {old['auc']:.2f} | {new['accuracy']:.2f} | {new['auc']:.2f} | {new['auc']-paper['auc']:+.2f} pp |")
    lines += ["", "## Table 2 — cross-dataset from the FF++ c23 checkpoint", "",
              "| Target | Paper AUC | RTX 5090 frame/video AUC | RTX 5060 Ti frame/video AUC |",
              "|---|---:|---:|---:|"]
    for name, row in result["table2"].items():
        old, new = row["rtx5090_historical"], row["rtx5060ti_current"]
        lines.append(f"| {name} | {row['paper_auc']:.2f} | {old['frame_auc']:.2f} / {old['video_auc']:.2f} | {new['frame_auc']:.2f} / {new['video_auc']:.2f} |")
    direct = result["celebdf_official_direct_diagnostic"]
    lines += ["", "For strict comparison with RTX 5090, the Celeb-DF row uses the same 16,420-frame manifest. "
              f"The separately preserved official-direct pipeline has {direct['frames']:,} frames and "
              f"{100*direct['video_auc']:.2f}% video AUC.", "", "## Table 3 — cross-manipulation", ""]
    table3 = result["table3"]
    lines += render_matrix("Paper", "paper", table3)
    lines += render_matrix("Historical RTX 5090", "rtx5090_historical", table3)
    lines += render_matrix("Current RTX 5060 Ti", "rtx5060ti_current", table3)
    lines += ["## Table 3 overall", "", "| Source | All 16 cells | Unseen 12 cells |", "|---|---:|---:|",
              f"| Paper | {table3['overall_all_cells']['paper']:.2f} | {table3['overall_unseen_only_derived']['paper']:.2f} |",
              f"| Historical RTX 5090 | {table3['overall_all_cells']['rtx5090_historical']:.2f} | {table3['overall_unseen_only_derived']['rtx5090_historical']:.2f} |",
              f"| Current RTX 5060 Ti | {table3['overall_all_cells']['rtx5060ti_current']:.2f} | {table3['overall_unseen_only_derived']['rtx5060ti_current']:.2f} |", ""]
    return "\n".join(lines)


def update_status(result: dict) -> None:
    table1 = result["table1"]
    lines = ["# Current WGN reproduction status", "", "**Machine:** NVIDIA RTX 5060 Ti 16 GB", "",
             f"**Completed:** {result['completed_at']}", "", "All paper-aligned Table 1, Table 2, and Table 3 protocols are complete.", "",
             "| Table 1 experiment | Frame ACC | Frame AUC |", "|---|---:|---:|"]
    for name, row in table1.items():
        current = row["rtx5060ti_current"]
        lines.append(f"| {name} | {current['accuracy']:.2f}% | {current['auc']:.2f}% |")
    lines += ["", "Full comparison: [CURRENT-FULL-REPRODUCTION.md](CURRENT-FULL-REPRODUCTION.md)", "",
              "The EXP-003 same-checkpoint c40/FaceShifter robustness sweep is a separate protocol and is not used as Table 1 reproduction.", ""]
    (REPRODUCTION / "CURRENT-REPRODUCTION-STATUS.md").write_text("\n".join(lines), encoding="utf-8")


def git(*arguments: str, timeout: int = 900) -> str:
    environment = os.environ.copy()
    environment.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    result = subprocess.run([str(GIT), "-c", "safe.directory=C:/sp/special_project",
                             "-c", "user.name=Codex", "-c", "user.email=codex@openai.com",
                             "-C", str(REPO), *arguments], capture_output=True, text=True,
                            timeout=timeout, env=environment)
    if result.returncode:
        raise RuntimeError(f"git {arguments[0]} failed: {result.stderr[-2000:]}")
    return result.stdout.strip()


def publish_git() -> None:
    if git("branch", "--show-current") != "main":
        raise RuntimeError("Publication requires main")
    git("add", "-f", "--", ARTIFACTS.relative_to(REPO).as_posix())
    git("add", "--", REPORT.relative_to(REPO).as_posix(),
        (REPRODUCTION / "CURRENT-FULL-REPRODUCTION.json").relative_to(REPO).as_posix(),
        (REPRODUCTION / "CURRENT-REPRODUCTION-STATUS.md").relative_to(REPO).as_posix())
    if git("diff", "--cached", "--name-only"):
        git("commit", "-m", "Complete current WGN three-table reproduction")
    commit = git("rev-parse", "HEAD")
    git("push", "origin", "HEAD:refs/heads/main")
    remote = git("ls-remote", "origin", "refs/heads/main").split()[0]
    if remote != commit:
        raise RuntimeError("Remote main verification failed")
    atomic_json(RUNS / "github-upload.json", {"status": "uploaded", "commit": commit, "branch": "main"})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--no-publish", action="store_true")
    args = parser.parse_args()
    runner = Runner(args.interval, args.no_publish)
    try:
        runner.execute()
    except Exception as error:
        runner.update("failed", error=repr(error))
        runner.event(f"RUNNER_FAILED {error!r}")
        raise
    finally:
        runner.close()


if __name__ == "__main__":
    main()

