"""Run locked cross-manipulation matrices for EXP-003 finalists."""
from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timedelta, timezone
import json
import msvcrt
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import yaml


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
MAIN_RUNS = Path('C:/sp/runs/wgn_overnight')
RUNS = Path('C:/sp/runs/wgn_selected_cross')
EXP2_RUNS = Path('C:/sp/runs/wgn_reproduction_current')
EXP2_FULL_RUNS = Path('C:/sp/runs/wgn_reproduction_table1')
SELECTION = MAIN_RUNS / 'SELECTION.json'
TZ = timezone(timedelta(hours=7))
GROUPS = {'df': 'FF-DF', 'f2f': 'FF-F2F', 'fs': 'FF-FS', 'nt': 'FF-NT'}


def now():
    return datetime.now(TZ).isoformat(timespec='seconds')


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f'.tmp.{os.getpid()}')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    for attempt in range(30):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(min(.01 * (attempt + 1), .25))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


class Runner:
    def __init__(self, interval):
        RUNS.mkdir(parents=True, exist_ok=True)
        (RUNS / 'logs').mkdir(exist_ok=True)
        self.interval = interval
        self.lock = (RUNS / 'runner.lock').open('a+b')
        self.lock.seek(0)
        if not self.lock.read(1):
            self.lock.write(b'0')
            self.lock.flush()
        self.lock.seek(0)
        msvcrt.locking(self.lock.fileno(), msvcrt.LK_NBLCK, 1)
        self.status_path = RUNS / 'status.json'
        self.state = read_json(self.status_path)
        self.state.setdefault('stages', {})
        self.state.pop('error', None)
        self.state['pid'] = os.getpid()
        (RUNS / 'runner.pid').write_text(str(os.getpid()), encoding='ascii')
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)

    def close(self):
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        self.lock.close()

    def update(self, phase, **values):
        if phase != 'failed':
            self.state.pop('error', None)
        self.state.update(updated_at=now(), phase=phase, **values)
        atomic_json(self.status_path, self.state)

    def event(self, message):
        line = f'{now()} {message}'
        print(line, flush=True)
        with (RUNS / 'events.log').open('a', encoding='utf-8') as handle:
            handle.write(line + '\n')

    def wait_for_turn(self):
        previous = None
        while True:
            selection = read_json(SELECTION)
            candidates = selection.get('recommended_cross_manipulation', [])
            selection_status = selection.get('status', 'unavailable')
            exp2 = read_json(EXP2_RUNS / 'status.json')
            exp2_phase = exp2.get('phase', 'unavailable')
            exp2_full = read_json(EXP2_FULL_RUNS / 'status.json')
            exp2_full_phase = exp2_full.get('phase', 'unavailable')
            observation = (selection_status, tuple(candidates), exp2_phase, exp2_full_phase)
            if observation != previous:
                self.event(f'WAIT selection={selection_status} candidates={candidates} '
                           f'exp2_table3={exp2_phase} exp2_full={exp2_full_phase}')
                previous = observation
            if selection_status == 'complete' and not candidates:
                self.update('complete_no_candidate', selected_candidates=[])
                self.event('NO_ELIGIBLE_CANDIDATE; CROSS_MANIPULATION_NOT_RUN')
                return []
            if selection_status == 'complete' and candidates and exp2_full_phase == 'complete':
                self.event(f'START_SELECTED_CROSS candidates={candidates}')
                return candidates
            self.update('waiting', selection_status=selection_status,
                        selected_candidates=candidates, exp2_phase=exp2_phase,
                        exp2_full_phase=exp2_full_phase)
            time.sleep(self.interval)

    def run_command(self, stage, arguments):
        if self.state['stages'].get(stage, {}).get('status') == 'complete':
            self.event(f'SKIP_COMPLETE {stage}')
            return
        log = RUNS / 'logs' / f'{stage}.log'
        environment = os.environ.copy()
        environment.update(TORCH_HOME='C:/sp/.cache/torch', HF_HOME='C:/sp/.cache/huggingface',
                           PYTHONUNBUFFERED='1', GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
        for attempt in range(1, 3):
            self.state['stages'][stage] = {'status': 'running', 'attempt': attempt,
                                                   'started_at': now(), 'log': str(log)}
            self.update(stage)
            self.event(f'START {stage} attempt={attempt}')
            with log.open('a', encoding='utf-8') as handle:
                handle.write('\nCOMMAND ' + json.dumps([str(value) for value in arguments]) + '\n')
                handle.flush()
                process = subprocess.Popen([str(value) for value in arguments], cwd=ROOT,
                                           env=environment, stdout=handle, stderr=subprocess.STDOUT)
                self.state['stages'][stage]['child_pid'] = process.pid
                while process.poll() is None:
                    self.update(stage)
                    time.sleep(10)
            status = 'complete' if process.returncode == 0 else 'failed'
            self.state['stages'][stage].update(status=status, returncode=process.returncode, ended_at=now())
            self.update(stage)
            self.event(f'{status.upper()} {stage} exit={process.returncode}')
            if process.returncode == 0:
                return
        raise RuntimeError(f'{stage} failed twice; inspect {log}')

    def config(self, method, slug, group):
        source = ROOT / 'configs' / f'{method}.yaml'
        if not source.exists():
            raise FileNotFoundError(f'Missing finalist config: {source}')
        config = yaml.safe_load(source.read_text(encoding='utf-8'))
        config['experiment'] = f'WGN_cross_{method}_{slug}'
        config['data']['manipulations'] = [group]
        destination = RUNS / 'configs' / f'{method}_{slug}.yaml'
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
        return destination

    def execute(self):
        candidates = self.wait_for_turn()
        if not candidates:
            return
        for method in candidates:
            for slug, group in GROUPS.items():
                config = self.config(method, slug, group)
                run = MAIN_RUNS / f'cross_{method}_{slug}_final'
                prefix = f'{method}_{slug}'
                self.run_command(f'smoke_{prefix}', [sys.executable, ROOT / 'smoke_test.py',
                                 '--config', config, '--output', RUNS / 'smoke' / f'{prefix}.json'])
                self.run_command(f'train_{prefix}', [sys.executable, ROOT / 'train.py', '--config', config,
                                 '--output-dir', run, '--resume'])
                self.run_command(f'evaluate_{prefix}', [sys.executable, ROOT / 'evaluate_cross_manipulation.py',
                                 '--config', config, '--run', run])
                shutil.copy2(RUNS / 'logs' / f'train_{prefix}.log', run / 'training.log')
                shutil.copy2(RUNS / 'logs' / f'evaluate_{prefix}.log', run / 'evaluation.log')
                self.run_command(f'publish_{prefix}', [sys.executable, ROOT / 'publish.py', '--run', run])
        self.update('complete', selected_candidates=candidates)
        self.event('SELECTED_CROSS_MANIPULATION_COMPLETE')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=30)
    args = parser.parse_args()
    runner = Runner(args.interval)
    try:
        runner.execute()
    except Exception as error:
        runner.update('failed', error=repr(error))
        runner.event(f'RUNNER_FAILED {error!r}')
        raise
    finally:
        runner.close()


if __name__ == '__main__':
    main()
