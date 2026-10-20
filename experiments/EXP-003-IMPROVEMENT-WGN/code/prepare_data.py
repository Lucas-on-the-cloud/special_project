"""Prepare the approved official FF++ crops with frozen preprocessing code."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import msvcrt
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
BASE = REPO/'experiments'/'EXP-002-WGN'/'reproduction'/'code'
DATA = Path('C:/sp/data')
RUNS = Path('C:/sp/runs/wgn_overnight')
GROUPS = ['FF-real', 'FF-DF', 'FF-F2F', 'FF-FS', 'FF-NT']


def already_prepared(compression, groups):
    """Return true when the shared manifest already contains the requested crops."""
    manifest = DATA/'FaceForensics++-official.json'
    if not manifest.exists():
        return False
    try:
        root = json.loads(manifest.read_text())['FaceForensics++']
        return all(
            root[group][split][compression]
            for group in groups
            for split in ('train', 'val', 'test')
        )
    except (KeyError, TypeError, ValueError):
        return False


def command_run(command, log):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('a', encoding='utf-8') as handle:
        handle.write('\nCOMMAND '+json.dumps([str(c) for c in command])+'\n')
        handle.flush()
        completed = subprocess.run([str(c) for c in command], stdout=handle, stderr=subprocess.STDOUT)
    if completed.returncode:
        raise RuntimeError(f'Command failed ({completed.returncode}); see {log}')


def prepare(compression, groups, workers=2, device='cuda', cpu_threads=8):
    if already_prepared(compression, groups):
        print(f'ALREADY_PREPARED {compression} groups={",".join(groups)}', flush=True)
        return
    command_run([sys.executable, ROOT/'download_ffpp.py', '--compression', compression,
                 '--groups', *groups, '--workers', '12'], RUNS/'logs'/f'download_{compression}.log')

    def preprocess(group):
        partial = DATA/'ffpp-manifests'/f'{compression}_{group}.json'
        partial.parent.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, BASE/'preprocess_ffpp_official.py',
                   '--input-root', DATA/'FaceForensics++-official',
                   '--output-root', DATA/'FaceForensics++-official-processed',
                   '--data-root', DATA, '--split-root', BASE/'splits', '--manifest', partial,
                   '--compressions', compression, '--groups', group,
                   '--detector-size', '512', '--batch-size', '16', '--device', device,
                   '--cpu-threads', str(cpu_threads)]
        command_run(command, RUNS/'logs'/f'preprocess_{compression}_{group}.log')
        return partial

    partials = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(preprocess, group) for group in groups]
        for future in as_completed(futures):
            partials.append(future.result())
    manifest = DATA/'FaceForensics++-official.json'
    payload = json.loads(manifest.read_text()) if manifest.exists() else {'FaceForensics++': {}}
    for partial in partials:
        content = json.loads(partial.read_text())['FaceForensics++']
        for group, splits in content.items():
            for split, compressions in splits.items():
                for name, videos in compressions.items():
                    payload['FaceForensics++'].setdefault(group, {}).setdefault(split, {})[name] = videos
    temporary = manifest.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    temporary.replace(manifest)
    print(f'PREPARED {compression} {manifest}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--compression', choices=['c23', 'c40'], default='c23')
    parser.add_argument('--groups', nargs='+', default=GROUPS)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--device', choices=['cuda', 'cpu'], default='cuda')
    parser.add_argument('--cpu-threads', type=int, default=8)
    args = parser.parse_args()
    lock_path = RUNS/'prepare-data.lock'
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open('a+b') as lock:
        lock.seek(0)
        if not lock.read(1):
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        print(f'WAITING_FOR_PREP_LOCK {lock_path}', flush=True)
        msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        try:
            print(f'ACQUIRED_PREP_LOCK {lock_path}', flush=True)
            prepare(args.compression, args.groups, args.workers, args.device, args.cpu_threads)
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


if __name__ == '__main__':
    main()
