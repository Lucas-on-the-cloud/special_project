"""Restart the private processed-data uploader until remote verification completes."""
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
RUNNER = CODE / "backup_processed_data_to_hf.py"
WORK = Path("C:/sp/data-handoff")
STATUS = WORK / "upload-status.json"
PID_FILE = WORK / "uploader.pid"
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


def current_pid(state):
    pid = state.get("pid")
    if isinstance(pid, int):
        return pid
    try:
        return int(PID_FILE.read_text(encoding="ascii").strip())
    except (FileNotFoundError, ValueError, OSError):
        return None


def write_status(phase, runner_pid, restarts, observation):
    path = WORK / "watchdog-status.json"
    temporary = path.with_suffix(f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps({"updated_at": now(), "pid": os.getpid(), "phase": phase,
                         "observation": observation, "runner_pid": runner_pid,
                         "restarts": restarts}, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--max-restarts", type=int, default=20)
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    lock = (WORK / "watchdog.lock").open("a+b")
    lock.seek(0)
    if not lock.read(1):
        lock.write(b"0"); lock.flush()
    lock.seek(0)
    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
    (WORK / "watchdog.pid").write_text(str(os.getpid()), encoding="ascii")
    restarts = 0
    while True:
        state = read_json(STATUS)
        pid = current_pid(state)
        if state.get("status") == "complete":
            write_status("complete", pid, restarts, "remote_verified")
            return
        if process_alive(pid):
            write_status("monitoring", pid, restarts, state.get("status", "unknown"))
            time.sleep(args.interval)
            continue
        if restarts >= args.max_restarts:
            write_status("restart_limit_reached", pid, restarts, state.get("status", "unknown"))
            raise RuntimeError("Private data uploader restart limit reached")
        stdout = (WORK / "uploader.stdout.log").open("ab", buffering=0)
        stderr = (WORK / "uploader.stderr.log").open("ab", buffering=0)
        environment = os.environ.copy()
        environment["HF_XET_HIGH_PERFORMANCE"] = "1"
        flags = (subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS |
                 subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        process = subprocess.Popen([sys.executable, str(RUNNER), "--repo-id",
                                    "lucashwang0102/wgn-private-data", "--shard-gib", "3"],
                                   cwd=CODE, env=environment, stdout=stdout, stderr=stderr,
                                   stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
        stdout.close(); stderr.close()
        PID_FILE.write_text(str(process.pid), encoding="ascii")
        restarts += 1
        with (WORK / "watchdog.log").open("a", encoding="utf-8") as handle:
            handle.write(f"{now()} RUNNER_START pid={process.pid} restart={restarts}\n")
        write_status("monitoring", process.pid, restarts, "runner_restarted")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

