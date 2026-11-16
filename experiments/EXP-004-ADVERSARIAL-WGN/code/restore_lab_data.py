"""Restore locked FF++ development/test and external test crops outside Git.

Archives are retained, SHA-verified before extraction, and resumable. Only
manifest-listed regular files are copied; no tar links or arbitrary paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import time

from huggingface_hub import get_token, hf_hub_url
from PIL import Image
import requests

REPO = 'lucashwang0102/wgn-private-data'
REVISION = 'e83e1c1d0b763f7fe324c5b57cd4c21e5f1529a2'
EXTERNAL_GROUPS = {
    'dfdc': ('DFDC.json', 'DFDC', ('DFDC_Real', 'DFDC_Fake')),
    'celebdf_official_direct': ('Celeb-DF-v2-official-direct.json', 'Celeb-DF-v2-official-direct',
                              ('CelebDFv2Official_real', 'CelebDFv2Official_fake')),
    'wilddeepfake': ('WildDeepfake.json', 'WildDeepfake', ('WildDeepfake_Real', 'WildDeepfake_Fake')),
}


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_relative(raw):
    path = PurePosixPath(raw.replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or not path.parts or ':' in path.parts[0]:
        raise ValueError('Unsafe manifest/archive path')
    return path.as_posix()


def frame_paths(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'frames':
                yield from (safe_relative(x) for x in child)
            else:
                yield from frame_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from frame_paths(child)


def download(session, remote, target):
    """Resume interrupted HTTP transfers, including partial CDN responses."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        return
    temporary = target.with_suffix(target.suffix + '.partial')
    url = hf_hub_url(REPO, remote, repo_type='dataset', revision=REVISION)
    failures = 0
    while True:
        offset = temporary.stat().st_size if temporary.exists() else 0
        try:
            with session.get(url, params={'download':'true', 'restore_offset':str(offset)},
                             headers={'Range':f'bytes={offset}-'} if offset else {},
                             stream=True, timeout=(30, 120)) as response:
                response.raise_for_status()
                content_range = response.headers.get('Content-Range', '')
                if response.status_code == 206:
                    start = int(content_range.split(' ')[1].split('-')[0])
                    if start != offset:
                        raise ValueError('Server returned an unexpected byte range')
                    total = int(content_range.rsplit('/', 1)[1])
                else:
                    offset = 0
                    total = int(response.headers['Content-Length']) if response.headers.get('Content-Length') else None
                downloaded = offset
                with temporary.open('ab' if offset else 'wb') as stream:
                    for block in response.iter_content(4 * 1024 * 1024):
                        stream.write(block)
                        downloaded += len(block)
            if total is None or downloaded == total:
                temporary.replace(target)
                return
            if downloaded > total:
                raise ValueError('Download exceeded declared size')
        except requests.RequestException as error:
            failures += 1
            if failures >= 5:
                raise RuntimeError(f'Download failed for {remote}: {type(error).__name__}') from None
            time.sleep(min(2 ** failures, 20))


def extract_selected(archive, destination, wanted):
    copied = 0
    with tarfile.open(archive, 'r:') as stream:
        for member in stream:
            name = safe_relative(member.name)
            if name not in wanted:
                continue
            if not member.isfile():
                raise ValueError('Manifest entry is not a regular archive file')
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != destination.parent):
                raise ValueError('Refusing a symlink in output path')
            temporary = target.with_suffix(target.suffix + '.partial')
            with stream.extractfile(member) as source, temporary.open('wb') as out:
                shutil.copyfileobj(source, out)
            if temporary.stat().st_size != member.size:
                raise ValueError('Extracted size mismatch')
            temporary.replace(target)
            copied += 1
    return copied


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--datasets', nargs='+', choices=['ffpp', *EXTERNAL_GROUPS], default=['ffpp', 'dfdc'])
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    if (runtime/'.git').exists() or any((p/'.git').exists() for p in runtime.parents):
        raise ValueError('Runtime must be outside a Git checkout')
    data = runtime/'data'
    cache = runtime/'data-archives'
    session = requests.Session()
    token = get_token()
    if token:
        session.headers['Authorization'] = 'Bearer ' + token
    download(session, 'SHA256SUMS.txt', cache/'SHA256SUMS.txt')
    expected = {}
    for line in (cache/'SHA256SUMS.txt').read_text().splitlines():
        checksum, remote = line.split(maxsplit=1)
        expected[safe_relative(remote.strip())] = checksum
    output = runtime/'data-restoration.json'
    status = json.loads(output.read_text()) if output.exists() else {'repo_id':REPO, 'revision':REVISION, 'groups':{}}
    if status['repo_id']!=REPO or status['revision']!=REVISION:
        raise ValueError('Existing restoration uses a different source revision')
    status['complete'] = False
    for group in args.datasets:
        filename = 'FaceForensics++-official.json' if group == 'ffpp' else EXTERNAL_GROUPS[group][0]
        download(session, 'metadata/'+filename, data/filename)
        payload = json.loads((data/filename).read_text())
        if group == 'ffpp':
            selected = [payload['FaceForensics++'][g][s]['c23']
                        for g in ['FF-real','FF-DF','FF-F2F','FF-FS','FF-NT'] for s in ['val','test']]
        else:
            _, dataset_name, groups = EXTERNAL_GROUPS[group]
            selected = [payload[dataset_name][g]['test'] for g in groups]
        wanted = set(frame_paths(selected))
        state = {'manifest_sha256':sha256(data/filename), 'selected_files':len(wanted),
                 'selection':'c23 val/test original four manipulations' if group == 'ffpp' else 'locked '+dataset_name+' test',
                 'verified_shards':[], 'verified_decoded_files':0, 'complete':False}
        status['groups'][group] = state
        for remote, checksum in sorted(expected.items()):
            if not remote.startswith('shards/'+group+'/'):
                continue
            archive = cache/remote
            print(json.dumps({'event':'downloading', 'shard':remote}), flush=True)
            download(session, remote, archive)
            if sha256(archive) != checksum:
                raise RuntimeError('Archive checksum mismatch: '+remote)
            copied = extract_selected(archive, data, wanted)
            state['verified_shards'].append({'path':remote,'sha256':checksum,'extracted':copied})
            output.write_text(json.dumps(status, indent=2)+'\n')
            print(json.dumps({'event':'verified_extracted','shard':remote,'selected_files':copied}), flush=True)
        for name in sorted(wanted):
            with Image.open(data/name) as image:
                image.load()
                if min(image.size)<1 or (group=='ffpp' and (image.mode!='RGB' or image.size!=(256,256))):
                    raise ValueError('Unexpected crop format: '+name)
                # DFDC uses the archived loader's RGB conversion and resize;
                # its source dimensions need not already be 256x256.
            state['verified_decoded_files'] += 1
        state['complete'] = True
        output.write_text(json.dumps(status, indent=2)+'\n')
        print(json.dumps({'event':'dataset_complete','group':group,'files':len(wanted)}), flush=True)
    status['complete'] = True
    output.write_text(json.dumps(status, indent=2)+'\n')
    print('RESTORE_COMPLETE '+str(output), flush=True)


if __name__ == '__main__':
    main()
