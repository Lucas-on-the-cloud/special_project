"""Download ONLY the author's official WildDeepfake real_test/fake_test shards."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import time
import urllib.request

DATA = Path('C:/sp/data')
ROOT = DATA/'WildDeepfake'
REPO = 'https://huggingface.co/datasets/xingjunm/WildDeepfake'


def download_shard(item):
    relative = item['path']
    target = ROOT/'archives'/Path(relative).relative_to('deepfake_in_the_wild')
    target.parent.mkdir(parents=True, exist_ok=True)
    marker = target.with_suffix('.sha256.json')
    if not (target.exists() and target.stat().st_size == item['size'] and marker.exists()):
        partial = target.with_suffix('.partial')
        command = ['curl.exe','-sS','-L','--fail','--connect-timeout','30','--max-time','1800',
                   '--retry','4','--retry-delay','5','-C','-','-o',str(partial),f'{REPO}/resolve/main/{relative}']
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode or not partial.exists() or partial.stat().st_size != item['size']:
            raise RuntimeError(f'{relative}: download failed {result.stderr[-300:]}')
        with partial.open('rb') as handle:
            digest = hashlib.file_digest(handle,'sha256').hexdigest()
        expected = item.get('lfs',{}).get('oid')
        if expected and digest != expected:
            raise ValueError(f'Checksum mismatch {relative}')
        partial.replace(target)
        marker.write_text(json.dumps({'url': f'{REPO}/resolve/main/{relative}', 'sha256': digest,
                                      'bytes': item['size']}))
    split = Path(relative).parent.name
    destination = ROOT/'extracted'/split/target.name.removesuffix('.tar.gz')
    done = destination/'.complete.json'
    if not done.exists():
        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(target,'r:*') as archive:
            for member in archive.getmembers():
                resolved = (destination/member.name).resolve()
                if not resolved.is_relative_to(destination.resolve()) or member.issym() or member.islnk():
                    raise ValueError(f'Unsafe archive member {member.name}')
            archive.extractall(destination, filter='data')
        done.write_text(json.dumps({'archive': str(target), 'bytes': item['size']}))
    return str(target)


def make_manifest():
    images = {'.png','.jpg','.jpeg'}
    payload = {'WildDeepfake': {}}
    total_sequences = 0
    for split, group in [('real_test','WildDeepfake_Real'),('fake_test','WildDeepfake_Fake')]:
        sequences = {}
        root = ROOT/'extracted'/split
        grouped = {}
        for path in root.rglob('*'):
            if path.is_file() and path.suffix.lower() in images:
                grouped.setdefault(path.parent,[]).append(path)
        for parent, frames in sorted(grouped.items()):
            identifier = str(parent.relative_to(root)).replace('\\','/')
            sequences[identifier] = {'label': group, 'frames': [str(p.relative_to(DATA)).replace('\\','/')
                                                              for p in sorted(frames)]}
        if not sequences:
            raise ValueError(f'No images for {split}')
        total_sequences += len(sequences)
        payload['WildDeepfake'][group] = {'train':{},'val':{},'test':sequences}
    path = DATA/'WildDeepfake.json'
    path.with_suffix('.tmp').write_text(json.dumps(payload,indent=2))
    path.with_suffix('.tmp').replace(path)
    print(f'WILD_MANIFEST_COMPLETE sequences={total_sequences}',flush=True)


def main():
    tasks = []
    for split in ('real_test','fake_test'):
        url = f'https://huggingface.co/api/datasets/xingjunm/WildDeepfake/tree/main/deepfake_in_the_wild/{split}?limit=1000&expand=false'
        tasks.extend(item for item in json.loads(urllib.request.urlopen(url,timeout=60).read())
                     if item['type']=='file' and item['path'].endswith('.tar.gz'))
    if not tasks:
        raise ValueError('No official test archives returned')
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT/'test-source-manifest.json').write_text(json.dumps(tasks,indent=2))
    failures = []
    print(f'WILD_DOWNLOAD_START shards={len(tasks)} GB={sum(t["size"] for t in tasks)/1e9:.2f}',flush=True)
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(download_shard,item):item['path'] for item in tasks}
        for number, future in enumerate(as_completed(futures),1):
            try:
                future.result()
                print(f'WILD_SHARD_COMPLETE {number}/{len(tasks)}',flush=True)
            except Exception as error:
                failures.append(str(error))
                print(f'WILD_SHARD_FAILED {error}',flush=True)
    (ROOT/'download-report.json').write_text(json.dumps({'shards':len(tasks),'failures':failures},indent=2))
    if failures:
        raise RuntimeError(f'{len(failures)} test shards failed')
    make_manifest()


if __name__ == '__main__':
    main()
