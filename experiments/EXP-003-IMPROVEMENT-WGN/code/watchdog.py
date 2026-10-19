"""Keep the unattended WGN queue alive without ever starting duplicate workers."""
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


ROOT = Path(__file__).resolve().parent
RUNS = Path('C:/sp/runs/wgn_overnight')
TZ = timezone(timedelta(hours=7))
STILL_ACTIVE = 259
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
TERMINAL_SUCCESS = {'queue_complete'}
RETRYABLE_TERMINAL = {'queue_finished_with_failures'}


def now():
    return datetime.now(TZ).isoformat(timespec='seconds')


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2), encoding='utf-8')
    for attempt in range(20):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 19:
                raise
            time.sleep(min(0.01 * (attempt + 1), 0.25))


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


class Watchdog:
    def __init__(self, interval, dead_grace, max_restarts):
        RUNS.mkdir(parents=True, exist_ok=True)
        self.interval = interval
        self.dead_grace = dead_grace
        self.max_restarts = max_restarts
        self.restarts = 0
        self.dead_since = None
        self.last_stall_notice = None
        self.lock = (RUNS/'watchdog.lock').open('a+b')
        self.lock.seek(0)
        if not self.lock.read(1):
            self.lock.write(b'0')
            self.lock.flush()
        self.lock.seek(0)
        msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        (RUNS/'watchdog.pid').write_text(str(os.getpid()), encoding='ascii')
        self.event(f'WATCHDOG_START pid={os.getpid()} interval={interval}s max_restarts={max_restarts}')

    def event(self, message):
        line = f'{now()} {message}'
        print(line, flush=True)
        with (RUNS/'watchdog.log').open('a', encoding='utf-8') as handle:
            handle.write(line+'\n')

    def read_queue(self):
        try:
            return json.loads((RUNS/'queue-status.json').read_text(encoding='utf-8'))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def write_status(self, phase, queue, observation):
        updated = queue.get('updated_at')
        heartbeat_age = None
        if updated:
            try:
                heartbeat_age = max(0, (datetime.now(TZ)-datetime.fromisoformat(updated)).total_seconds())
            except ValueError:
                pass
        atomic_json(RUNS/'watchdog-status.json', {
            'updated_at': now(), 'pid': os.getpid(), 'phase': phase,
            'queue_pid': queue.get('pid'), 'queue_phase': queue.get('phase'),
            'queue_heartbeat_age_seconds': heartbeat_age,
            'restarts': self.restarts, 'max_restarts': self.max_restarts,
            'observation': observation,
        })

    def active_child(self, queue):
        stage = queue.get('stages', {}).get(queue.get('phase'), {})
        pid = stage.get('child_pid')
        return pid if process_alive(pid) else None

    def start_queue(self):
        stdout = (RUNS/'queue.stdout.log').open('ab', buffering=0)
        stderr = (RUNS/'queue.stderr.log').open('ab', buffering=0)
        environment = os.environ.copy()
        environment.update(TORCH_HOME='C:/sp/.cache/torch', HF_HOME='C:/sp/.cache/huggingface',
                           PYTHONUNBUFFERED='1', GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        process = subprocess.Popen([sys.executable, str(ROOT/'run_queue.py')], cwd=ROOT,
                                   env=environment, stdout=stdout, stderr=stderr,
                                   stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
        stdout.close()
        stderr.close()
        (RUNS/'queue.pid').write_text(str(process.pid), encoding='ascii')
        self.restarts += 1
        self.dead_since = None
        self.event(f'QUEUE_RESTART pid={process.pid} restart={self.restarts}/{self.max_restarts}')

    def run(self):
        while True:
            queue = self.read_queue()
            queue_pid = queue.get('pid')
            alive = process_alive(queue_pid)
            phase = queue.get('phase', 'unknown')
            updated = queue.get('updated_at')
            heartbeat_age = None
            if updated:
                try:
                    heartbeat_age = (datetime.now(TZ)-datetime.fromisoformat(updated)).total_seconds()
                except ValueError:
                    pass

            if alive:
                self.dead_since = None
                observation = 'queue_alive'
                if heartbeat_age is not None and heartbeat_age > 180:
                    observation = 'queue_alive_heartbeat_stale'
                    stamp = int(time.time()//600)
                    if self.last_stall_notice != stamp:
                        self.event(f'HEARTBEAT_STALE queue_pid={queue_pid} age={heartbeat_age:.0f}s phase={phase}')
                        self.last_stall_notice = stamp
                self.write_status('monitoring', queue, observation)
                time.sleep(self.interval)
                continue

            if phase in TERMINAL_SUCCESS:
                self.write_status('complete', queue, 'queue_completed_successfully')
                self.event(f'WATCHDOG_COMPLETE queue_phase={phase}')
                return

            child = self.active_child(queue)
            if child:
                self.dead_since = None
                self.write_status('waiting_for_orphan', queue, f'child_pid_{child}_still_alive')
                time.sleep(self.interval)
                continue

            if self.restarts >= self.max_restarts:
                self.write_status('restart_limit_reached', queue, f'queue_dead_phase_{phase}')
                self.event(f'WATCHDOG_STOP restart_limit={self.max_restarts} queue_phase={phase}')
                return

            if self.dead_since is None:
                self.dead_since = time.monotonic()
                reason = 'retryable_failures' if phase in RETRYABLE_TERMINAL else 'queue_dead'
                self.event(f'QUEUE_DOWN phase={phase} reason={reason}; grace={self.dead_grace}s')
            elapsed = time.monotonic()-self.dead_since
            if elapsed < self.dead_grace:
                self.write_status('restart_grace', queue, f'restart_in_{max(0, self.dead_grace-elapsed):.0f}s')
                time.sleep(min(self.interval, self.dead_grace-elapsed))
                continue
            self.start_queue()
            time.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--dead-grace', type=int, default=90)
    parser.add_argument('--max-restarts', type=int, default=6)
    args = parser.parse_args()
    Watchdog(args.interval, args.dead_grace, args.max_restarts).run()


if __name__ == '__main__':
    main()
