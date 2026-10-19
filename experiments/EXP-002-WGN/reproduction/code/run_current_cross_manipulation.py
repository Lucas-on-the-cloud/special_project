"""Resume-safe current-machine WGN cross-manipulation reproduction."""
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
CONFIGS = CODE / "configs" / "current-rtx5060-cross-manipulation"
RUNS = Path("C:/sp/runs/wgn_reproduction_current")
IMPROVEMENT_RUNS = Path("C:/sp/runs/wgn_overnight")
ARTIFACTS = REPRODUCTION / "artifacts" / "current-cross-manipulation"
EVIDENCE = REPRODUCTION / "evidence" / "current-cross-manipulation"
HISTORICAL = REPRODUCTION / "evidence" / "rtx5090-historical-cross-manipulation" / "comparison.json"
GIT = Path("C:/sp/.tools/git-portable/cmd/git.exe")
TZ = timezone(timedelta(hours=7))
GROUPS = {"df": "FF-DF", "f2f": "FF-F2F", "fs": "FF-FS", "nt": "FF-NT"}
ORDER = list(GROUPS)
TARGETS = list(GROUPS.values())
STILL_ACTIVE = 259
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def atomic_json(path: Path, value) -> None:
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


class Runner:
    def __init__(self, poll_seconds: int, no_wait: bool, no_publish: bool):
        RUNS.mkdir(parents=True, exist_ok=True)
        (RUNS / "logs").mkdir(exist_ok=True)
        self.poll_seconds = poll_seconds
        self.no_wait = no_wait
        self.no_publish = no_publish
        self.lock = (RUNS / "runner.lock").open("a+b")
        self.lock.seek(0)
        if not self.lock.read(1):
            self.lock.write(b"0")
            self.lock.flush()
        self.lock.seek(0)
        msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        self.state_path = RUNS / "status.json"
        self.state = json.loads(self.state_path.read_text(encoding="utf-8")) if self.state_path.exists() else {}
        self.state.setdefault("stages", {})
        self.state["pid"] = os.getpid()
        (RUNS / "runner.pid").write_text(str(os.getpid()), encoding="ascii")
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

    def close(self):
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)

    def update(self, phase: str, **values) -> None:
        self.state.update(updated_at=now(), phase=phase, **values)
        atomic_json(self.state_path, self.state)

    def event(self, message: str) -> None:
        line = f"{now()} {message}"
        print(line, flush=True)
        with (RUNS / "events.log").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def run_command(self, stage: str, arguments: list, cwd: Path = EXP3_CODE) -> None:
        if self.state["stages"].get(stage, {}).get("status") == "complete":
            self.event(f"SKIP_COMPLETE {stage}")
            return
        log = RUNS / "logs" / f"{stage}.log"
        environment = os.environ.copy()
        environment.update(TORCH_HOME="C:/sp/.cache/torch", HF_HOME="C:/sp/.cache/huggingface",
                           PYTHONUNBUFFERED="1", GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
        for attempt in range(1, 3):
            self.state["stages"][stage] = {"status": "running", "started_at": now(),
                                                   "log": str(log), "attempt": attempt}
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
            self.state["stages"][stage].update(status=status, ended_at=now(), returncode=process.returncode)
            self.update(stage)
            self.event(f"{status.upper()} {stage} exit={process.returncode}")
            if process.returncode == 0:
                return
        raise RuntimeError(f"{stage} failed twice; inspect {log}")

    def wait_for_improvements(self) -> None:
        if self.no_wait:
            self.event("IMPROVEMENT_QUEUE_WAIT_BYPASSED")
            return
        last_notice = None
        while True:
            try:
                queue = json.loads((IMPROVEMENT_RUNS / "queue-status.json").read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                queue = {}
            phase = queue.get("phase", "unavailable")
            queue_pid = queue.get("pid")
            degradation = queue.get("stages", {}).get("degradation_consistency_final", {}).get("status")
            if phase == "queue_complete" and not process_alive(queue_pid):
                self.event("IMPROVEMENT_QUEUE_COMPLETE; STARTING_EXP002_CROSS_MANIPULATION")
                return
            notice = (phase, degradation, queue_pid)
            if notice != last_notice:
                self.event(f"WAIT improvement_phase={phase} degradation_consistency={degradation} pid={queue_pid}")
                last_notice = notice
            self.update("waiting_for_improvement_queue", improvement_phase=phase,
                        degradation_consistency=degradation, improvement_pid=queue_pid)
            time.sleep(self.poll_seconds)

    def execute(self) -> None:
        self.wait_for_improvements()
        for slug in ORDER:
            config = CONFIGS / f"{slug}.yaml"
            run = RUNS / f"{slug}_final"
            self.run_command(f"smoke_{slug}", [sys.executable, EXP3_CODE / "smoke_test.py",
                             "--config", config, "--output", RUNS / "smoke" / f"{slug}.json"])
            self.run_command(f"train_{slug}", [sys.executable, EXP3_CODE / "train.py", "--config", config,
                             "--output-dir", run, "--resume"])
            self.run_command(f"evaluate_{slug}", [sys.executable, EXP3_CODE / "evaluate_cross_manipulation.py",
                             "--config", config, "--run", run])
        self.publish_results()
        self.update("complete")
        self.event("CURRENT_WGN_CROSS_MANIPULATION_COMPLETE")

    def publish_results(self) -> None:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        checksums = []
        for slug in ORDER:
            run = RUNS / f"{slug}_final"
            required = ("best.pt", "summary.json", "cross_manipulation.json")
            if not all((run / name).exists() for name in required):
                raise FileNotFoundError(f"Incomplete cross-manipulation run: {slug}")
            target, compact = ARTIFACTS / slug, EVIDENCE / slug
            target.mkdir(parents=True, exist_ok=True)
            compact.mkdir(parents=True, exist_ok=True)
            for name in ("best.pt", "summary.json", "resolved_config.yaml", "environment.json",
                         "metrics.jsonl", "cross_manipulation.json"):
                if (run / name).exists():
                    shutil.copy2(run / name, target / name)
            for name in ("summary.json", "cross_manipulation.json"):
                shutil.copy2(run / name, compact / name)
            digest = sha256(run / "best.pt")
            (target / "SHA256SUMS.txt").write_text(f"{digest}  best.pt\n", encoding="utf-8")
            checksums.append(f"{digest}  ../../artifacts/current-cross-manipulation/{slug}/best.pt")
        (EVIDENCE / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
        comparison = build_comparison()
        atomic_json(EVIDENCE / "comparison.json", comparison)
        report = render_markdown(comparison)
        (EVIDENCE / "README.md").write_text(report, encoding="utf-8")
        (EVIDENCE / "RESULTS.md").write_text(report, encoding="utf-8")
        update_status_document(comparison)
        if self.no_publish:
            self.event("PUBLICATION_SKIPPED_BY_ARGUMENT")
        else:
            publish_git()


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def current_rows() -> dict:
    labels = {"df": "DF", "f2f": "F2F", "fs": "FS", "nt": "NT"}
    rows = {}
    for slug in ORDER:
        payload = json.loads((RUNS / f"{slug}_final" / "cross_manipulation.json").read_text(encoding="utf-8"))
        rows[labels[slug]] = [100 * payload["results"][target]["auc"] for target in TARGETS]
        rows[labels[slug]].append(100 * payload["average_auc_including_diagonal"])
    return rows


def build_comparison() -> dict:
    historical = json.loads(HISTORICAL.read_text(encoding="utf-8"))
    current = current_rows()
    names = ("DF", "F2F", "FS", "NT")
    rows = {name: {"paper": historical["rows"][name]["paper"],
                   "rtx5090_historical": historical["rows"][name]["reproduction"],
                   "rtx5060ti_current": [round(value, 6) for value in current[name]]} for name in names}
    all_current = [value for row in current.values() for value in row[:4]]
    unseen = [current[name][column] for name in names for column in range(4) if column != names.index(name)]
    return {
        "paper_source": historical["paper_source"], "paper_table": 3,
        "metric": "frame-level AUC", "unit": "percent",
        "average_definition": "mean over DF, F2F, FS, and NT, including the training manipulation",
        "columns": ["DF", "F2F", "FS", "NT", "Avg"], "rows": rows,
        "overall_all_cells": {"paper": historical["overall_all_cells"]["paper"],
                              "rtx5090_historical": historical["overall_all_cells"]["reproduction"],
                              "rtx5060ti_current": round(sum(all_current) / len(all_current), 6)},
        "overall_unseen_only_derived": {"paper": historical["overall_unseen_only_derived"]["paper"],
                                        "rtx5090_historical": historical["overall_unseen_only_derived"]["reproduction"],
                                        "rtx5060ti_current": round(sum(unseen) / len(unseen), 6)},
        "completed_at": now(), "machine": "NVIDIA RTX 5060 Ti 16 GB",
    }


def render_matrix(title: str, key: str, comparison: dict) -> list[str]:
    lines = [f"### {title}", "", "| Train / Test | DF | F2F | FS | NT | Avg |",
             "|---|---:|---:|---:|---:|---:|"]
    for name in ("DF", "F2F", "FS", "NT"):
        values = comparison["rows"][name][key]
        lines.append("| " + name + " | " + " | ".join(f"{value:.2f}" for value in values) + " |")
    return lines + [""]


def render_markdown(comparison: dict) -> str:
    lines = ["# Current WGN cross-manipulation reproduction", "",
             "Four independent WGN models were trained for 25 epochs on one FF++ c23 manipulation and "
             "evaluated on all four manipulation test sets. Values are frame-level AUC (%).", ""]
    lines += render_matrix("Paper — Table 3", "paper", comparison)
    lines += render_matrix("Historical RTX 5090 reproduction", "rtx5090_historical", comparison)
    lines += render_matrix("Current RTX 5060 Ti reproduction", "rtx5060ti_current", comparison)
    lines += ["## Overall comparison", "", "| Source | All 16 cells | Unseen 12 cells (derived) |",
              "|---|---:|---:|",
              f"| Paper | {comparison['overall_all_cells']['paper']:.2f} | {comparison['overall_unseen_only_derived']['paper']:.2f} |",
              f"| Historical RTX 5090 | {comparison['overall_all_cells']['rtx5090_historical']:.2f} | {comparison['overall_unseen_only_derived']['rtx5090_historical']:.2f} |",
              f"| Current RTX 5060 Ti | {comparison['overall_all_cells']['rtx5060ti_current']:.2f} | {comparison['overall_unseen_only_derived']['rtx5060ti_current']:.2f} |", "",
              "The four current checkpoints and SHA-256 files are stored under "
              "`../../artifacts/current-cross-manipulation/`.", ""]
    return "\n".join(lines)


def update_status_document(comparison: dict) -> None:
    current = comparison["overall_all_cells"]["rtx5060ti_current"]
    unseen = comparison["overall_unseen_only_derived"]["rtx5060ti_current"]
    status = REPRODUCTION / "CURRENT-REPRODUCTION-STATUS.md"
    text = status.read_text(encoding="utf-8")
    marker = "## Pending"
    replacement = ("## Cross-manipulation completed\n\n"
                   f"- Current RTX 5060 Ti all-cell mean AUC: **{current:.2f}%**\n"
                   f"- Current RTX 5060 Ti unseen-only mean AUC: **{unseen:.2f}%**\n"
                   "- Four independently trained checkpoints: `artifacts/current-cross-manipulation/`\n"
                   "- Full comparison: `evidence/current-cross-manipulation/RESULTS.md`\n")
    if marker in text:
        head, tail = text.split(marker, 1)
        historical = tail.find("\nThe directory")
        suffix = tail[historical:] if historical >= 0 else ""
        text = head + replacement + suffix
    else:
        text += "\n\n" + replacement + "\n"
    status.write_text(text, encoding="utf-8")


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
        raise RuntimeError("Publication requires the main branch")
    git("add", "-f", "--", ARTIFACTS.relative_to(REPO).as_posix())
    git("add", "--", EVIDENCE.relative_to(REPO).as_posix(),
        (REPRODUCTION / "CURRENT-REPRODUCTION-STATUS.md").relative_to(REPO).as_posix())
    if git("diff", "--cached", "--name-only"):
        git("commit", "-m", "Complete current WGN cross-manipulation reproduction")
    commit = git("rev-parse", "HEAD")
    git("push", "origin", "HEAD:refs/heads/main")
    remote = git("ls-remote", "origin", "refs/heads/main").split()[0]
    if remote != commit:
        raise RuntimeError("Remote main verification failed")
    atomic_json(RUNS / "github-upload.json", {"status": "uploaded", "commit": commit, "branch": "main"})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--no-wait", action="store_true", help="Caller guarantees the GPU is idle")
    parser.add_argument("--no-publish", action="store_true")
    args = parser.parse_args()
    runner = Runner(args.poll_seconds, args.no_wait, args.no_publish)
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
