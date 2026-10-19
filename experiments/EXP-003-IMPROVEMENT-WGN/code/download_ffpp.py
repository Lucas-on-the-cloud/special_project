"""Resumable FF++ EU2 download using the approved official v4 file list/layout."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request

GROUPS = {'FF-real': 'original_sequences/youtube',
          'FF-DF': 'manipulated_sequences/Deepfakes',
          'FF-F2F': 'manipulated_sequences/Face2Face',
          'FF-FS': 'manipulated_sequences/FaceSwap',
          'FF-NT': 'manipulated_sequences/NeuralTextures',
          'FF-FSh': 'manipulated_sequences/FaceShifter'}
BASE = 'http://kaldir.vc.in.tum.de/faceforensics/v3/'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='C:/sp/data/FaceForensics++-official')
    parser.add_argument('--compression', default='c23', choices=['c23', 'c40'])
    parser.add_argument('--groups', nargs='+', default=list(GROUPS)[:5], choices=list(GROUPS))
    parser.add_argument('--workers', type=int, default=12)
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    pairs = json.loads(urllib.request.urlopen(BASE + 'misc/filelist.json', timeout=60).read())
    (root / 'official-filelist.json').write_text(json.dumps(pairs), encoding='utf-8')
    tasks = []
    for group in args.groups:
        names = [name for pair in pairs for name in pair] if group == 'FF-real' else [
            '_'.join(p) for pair in pairs for p in (pair, pair[::-1])]
        for name in names[:args.limit or None]:
            relative = f'{GROUPS[group]}/{args.compression}/videos/{name}.mp4'
            tasks.append(relative)
    curl = shutil.which('curl.exe') or shutil.which('curl')
    if not curl:
        raise RuntimeError('curl is required')
    started = time.monotonic()

    def download(relative):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        marker = target.with_suffix('.download.json')
        if target.exists() and marker.exists():
            recorded = json.loads(marker.read_text())
            if target.stat().st_size == recorded['bytes']:
                return relative, 'cached', target.stat().st_size
        temporary = target.with_suffix('.mp4.partial')
        for attempt in range(4):
            command = [curl, '-sS', '-L', '--fail', '--connect-timeout', '20', '--max-time', '900',
                       '--retry', '2', '--retry-delay', '3', '-C', '-', '-o', str(temporary), BASE + relative]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0 and temporary.exists():
                with temporary.open('rb') as handle:
                    header = handle.read(64)
                if b'ftyp' not in header:
                    raise RuntimeError(f'Not an MP4: {relative}')
                digest = hashlib.file_digest(temporary.open('rb'), 'sha256').hexdigest()
                temporary.replace(target)
                marker.write_text(json.dumps({'url': BASE + relative, 'bytes': target.stat().st_size,
                                              'sha256': digest}), encoding='utf-8')
                return relative, 'downloaded', target.stat().st_size
            if result.returncode == 33 and temporary.exists():
                temporary.unlink()  # Server cannot resume this task-owned partial file.
            time.sleep(2 ** attempt)
        raise RuntimeError(f'{relative}: {result.stderr[-500:]}')

    failures = []
    total_bytes = 0
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download, task): task for task in tasks}
        for number, future in enumerate(as_completed(futures), 1):
            try:
                relative, status, size = future.result()
                total_bytes += size
                if number % 25 == 0 or number == len(tasks):
                    print(json.dumps({'complete': number, 'total': len(tasks), 'GB': round(total_bytes/1e9, 2),
                                      'minutes': round((time.monotonic()-started)/60, 1)}), flush=True)
            except Exception as error:
                failures.append(str(error))
                print(f'DOWNLOAD_FAILED {error}', flush=True)
    report = {'tasks': len(tasks), 'failures': failures, 'bytes': total_bytes}
    (root / f'download-{args.compression}-report.json').write_text(json.dumps(report, indent=2))
    if failures:
        raise RuntimeError(f'{len(failures)} downloads failed; rerun to resume')
    print('DOWNLOAD_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
