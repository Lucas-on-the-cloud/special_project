"""Keep the selected EXP-003 cross-manipulation runner alive."""
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
RUNS = Path('C:/sp/runs/wgn_selected_cross')
TZ = timezone(timedelta(hours=7))
STILL_ACTIVE = 259
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def now():
    return datetime.now(TZ).isoformat(timespec='seconds')


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f'.tmp.{os.getpid()}')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    for attempt in range(30):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(min(.01 * (attempt + 1), .25))


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
    def __init__(self, interval, max_restarts):
        RUNS.mkdir(parents=True, exist_ok=True)
        self.interval, self.max_restarts, self.restarts = interval, max_restarts, 0
        self.lock = (RUNS / 'watchdog.lock').open('a+b')
        self.lock.seek(0)
        if not self.lock.read(1):
            self.lock.write(b'0')
            self.lock.flush()
        self.lock.seek(0)
        msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        (RUNS / 'watchdog.pid').write_text(str(os.getpid()), encoding='ascii')

    def event(self, message):
        line = f'{now()} {message}'
        print(line, flush=True)
        with (RUNS / 'watchdog.log').open('a', encoding='utf-8') as handle:
            handle.write(line + '\n')

    def status(self, phase, observation, runner):
        atomic_json(RUNS / 'watchdog-status.json', {
            'updated_at': now(), 'pid': os.getpid(), 'phase': phase,
            'observation': observation, 'runner_pid': runner.get('pid'),
            'runner_phase': runner.get('phase'), 'restarts': self.restarts,
            'max_restarts': self.max_restarts})

    def start(self):
        stdout = (RUNS / 'runner.stdout.log').open('ab', buffering=0)
        stderr = (RUNS / 'runner.stderr.log').open('ab', buffering=0)
        environment = os.environ.copy()
        environment.update(PYTHONUNBUFFERED='1', GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        process = subprocess.Popen([sys.executable, str(ROOT / 'run_selected_cross_manipulation.py')],
                                   cwd=ROOT, env=environment, stdout=stdout, stderr=stderr,
                                   stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
        stdout.close()
        stderr.close()
        self.restarts += 1
        self.event(f'RUNNER_START pid={process.pid} restart={self.restarts}/{self.max_restarts}')

    def run(self):
        self.event(f'WATCHDOG_START pid={os.getpid()} max_restarts={self.max_restarts}')
        while True:
            runner = read_json(RUNS / 'status.json')
            phase = runner.get('phase')
            if phase in {'complete', 'complete_no_candidate'}:
                self.status('complete', phase, runner)
                self.event(f'WATCHDOG_COMPLETE runner_phase={phase}')
                return
            if process_alive(runner.get('pid')):
                self.status('monitoring', 'runner_alive', runner)
                time.sleep(self.interval)
                continue
            if self.restarts >= self.max_restarts:
                self.status('restart_limit_reached', 'runner_dead', runner)
                self.event('WATCHDOG_STOP restart limit reached')
                return
            self.start()
            time.sleep(self.interval)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--max-restarts', type=int, default=20)
    args = parser.parse_args()
    Watchdog(args.interval, args.max_restarts).run()


if __name__ == '__main__':
    main()
