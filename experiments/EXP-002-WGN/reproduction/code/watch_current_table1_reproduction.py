"""Keep the current-machine Table 1 completion runner alive."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timedelta, timezone
import json
import msvcrt
import os
from pathlib import Path
import subprocess
import sys
import time


CODE = Path(__file__).resolve().parent
RUNS = Path("C:/sp/runs/wgn_reproduction_table1")
TZ = timezone(timedelta(hours=7))
STILL_ACTIVE = 259
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def now():
    return datetime.now(TZ).isoformat(timespec="seconds")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def process_alive(pid):
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


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--max-restarts", type=int, default=20)
    args = parser.parse_args()
    RUNS.mkdir(parents=True, exist_ok=True)
    lock = (RUNS / "watchdog.lock").open("a+b")
    lock.seek(0)
    if not lock.read(1):
        lock.write(b"0"); lock.flush()
    lock.seek(0)
    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    (RUNS / "watchdog.pid").write_text(str(os.getpid()), encoding="ascii")
    restarts = 0
    while True:
        state = read_json(RUNS / "status.json")
        phase = state.get("phase")
        if phase == "complete":
            atomic_json(RUNS / "watchdog-status.json", {"updated_at": now(), "phase": "complete", "restarts": restarts})
            return
        if not process_alive(state.get("pid")):
            if restarts >= args.max_restarts:
                raise RuntimeError("Table 1 runner restart limit reached")
            stdout = (RUNS / "runner.stdout.log").open("ab", buffering=0)
            stderr = (RUNS / "runner.stderr.log").open("ab", buffering=0)
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            process = subprocess.Popen([sys.executable, str(CODE / "run_current_table1_reproduction.py")],
                                       cwd=CODE, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL,
                                       creationflags=flags, close_fds=True)
            stdout.close(); stderr.close(); restarts += 1
            with (RUNS / "watchdog.log").open("a", encoding="utf-8") as handle:
                handle.write(f"{now()} RUNNER_START pid={process.pid} restart={restarts}\n")
        atomic_json(RUNS / "watchdog-status.json", {"updated_at": now(), "phase": "monitoring",
                    "runner_pid": read_json(RUNS / "status.json").get("pid"), "runner_phase": phase,
                    "restarts": restarts})
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

