"""Import user-downloaded RGB archives + matching manifests without changing splits."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path, PureWindowsPath
import shutil
import subprocess
import tarfile
import time
import zipfile

DATA = Path('C:/sp/data')
INCOMING = DATA/'incoming'
EXTRACTED = DATA/'external'
SPECS = {'Celeb-DF-v2': ('CelebDFv2_real','CelebDFv2_fake'), 'DFDC': ('DFDC_Real','DFDC_Fake')}


def digest(path):
    import hashlib
    with path.open('rb') as handle:
        return hashlib.file_digest(handle,'sha256').hexdigest()


def safe_target(destination, name):
    target = (destination/name.replace('\\','/')).resolve()
    if not target.is_relative_to(destination.resolve()):
        raise ValueError(f'Unsafe archive path {name}')
    return target


def extract(path):
    destination = EXTRACTED/path.name.replace('.tar.gz','').replace('.zip','').replace('.tar','').replace('.7z','')
    marker = destination/'.archive_complete.json'
    if marker.exists():
        return
    destination.mkdir(parents=True, exist_ok=True)
    if path.name.endswith('.zip'):
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                safe_target(destination, member.filename)
                if (member.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Archive symlinks are not supported')
            archive.extractall(destination)
    elif path.name.endswith(('.tar','.tar.gz','.tgz')):
        with tarfile.open(path,'r:*') as archive:
            for member in archive.getmembers():
                safe_target(destination,member.name)
                if member.issym() or member.islnk():
                    raise ValueError('Archive links are not supported')
            archive.extractall(destination,filter='data')
    elif path.name.endswith('.7z'):
        executable = 'C:/Program Files/7-Zip/7z.exe'
        listing = subprocess.check_output([executable,'l','-slt',str(path)],text=True)
        for line in listing.split('----------')[-1].splitlines():
            if line.startswith('Path = '):
                safe_target(destination,line[7:])
            if line.startswith(('Symbolic Link = ','Hard Link = ')):
                raise ValueError('Archive links are not supported')
        subprocess.run([executable,'x','-y',f'-o{destination}',str(path)],check=True,stdout=subprocess.DEVNULL)
    else:
        return
    marker.write_text(json.dumps({'archive':path.name,'sha256':digest(path),'bytes':path.stat().st_size}))
    print(f'EXTRACTED {path.name}',flush=True)


def import_once():
    INCOMING.mkdir(parents=True,exist_ok=True)
    EXTRACTED.mkdir(parents=True,exist_ok=True)
    # Never touch a browser partial download. A completed archive must also be stable for 30s.
    archive_candidates=list(INCOMING.rglob('*'))+list(EXTRACTED.rglob('*'))+list(DATA.glob('*'))
    for path in archive_candidates:
        if 'Celeb-DF-v1' in path.name:
            continue
        if path.is_file() and path.name.endswith(('.zip','.tar','.tar.gz','.tgz','.7z')):
            if time.time()-path.stat().st_mtime >= 30:
                extract(path)
    sources = []
    source_candidates=list(INCOMING.rglob('*.json'))+list(EXTRACTED.rglob('*.json'))+list(DATA.glob('*.json'))
    for path in source_candidates:
        if path.name.startswith('.'):
            continue
        try:
            document = json.loads(path.read_text(encoding='utf-8-sig'))
        except (ValueError,UnicodeError):
            continue
        for dataset in SPECS:
            if dataset in document:
                sources.append((dataset,path,document))
    def ready(name):
        path=DATA/f'{name}.json'
        if not path.exists():
            return False
        try:
            content=json.loads(path.read_text(encoding='utf-8-sig'))[name]
            for group in SPECS[name]:
                if not content[group]['test']:
                    return False
                for item in content[group]['test'].values():
                    for relative in item['frames']:
                        if not DATA.joinpath(*PureWindowsPath(relative).parts).is_file():
                            return False
            return True
        except (ValueError,KeyError):
            return False
    pending = [item for item in sources if not ready(item[0])]
    if not pending:
        return {name: ready(name) for name in SPECS}
    suffix_index = defaultdict(list)
    for root in (INCOMING,EXTRACTED):
        for path in root.rglob('*'):
            if path.is_file() and path.suffix.lower() in ('.png','.jpg','.jpeg'):
                suffix_index[tuple(part.lower() for part in path.parts[-3:])].append(path)

    def resolve(relative):
        pieces = PureWindowsPath(relative).parts
        candidates = suffix_index.get(tuple(part.lower() for part in pieces[-3:]),[])
        ranked = []
        for candidate in candidates:
            overlap = 0
            for actual, expected in zip(reversed(candidate.parts),reversed(pieces)):
                if actual.lower() != expected.lower():
                    break
                overlap += 1
            ranked.append((overlap,candidate))
        if not ranked:
            raise FileNotFoundError(relative)
        ranked.sort(key=lambda item:item[0],reverse=True)
        if len(ranked)>1 and ranked[0][0] == ranked[1][0]:
            raise ValueError(f'Ambiguous frame path: {relative}')
        return ranked[0][1]

    for dataset,path,document in pending:
        try:
            root = document[dataset]
            selected = {}
            total_frames, total_videos = 0,0
            for group in SPECS[dataset]:
                videos = root[group]['test']
                if not videos:
                    raise ValueError(f'Empty test group {group}')
                selected[group] = {'train':{},'val':{},'test':{}}
                for video, item in videos.items():
                    frames = [str(resolve(frame).relative_to(DATA)).replace('\\','/') for frame in item['frames']]
                    if not frames:
                        raise ValueError(f'No frames for {video}')
                    selected[group]['test'][video] = {'label':group,'frames':frames}
                    total_frames += len(frames)
                    total_videos += 1
            if dataset == 'Celeb-DF-v2' and total_videos != 518:
                raise ValueError(f'Expected official 518 Celeb-DF v2 test videos; got {total_videos}')
            output = DATA/f'{dataset}.json'
            if path.resolve()==output.resolve():
                backup=DATA/'source-manifests'/path.name
                backup.parent.mkdir(exist_ok=True)
                if not backup.exists():
                    shutil.copy2(path,backup)
                path=backup
            output.with_suffix('.tmp').write_text(json.dumps({dataset:selected},indent=2))
            output.with_suffix('.tmp').replace(output)
            output.with_suffix('.source.json').write_text(json.dumps({'source_manifest':str(path),
                       'source_sha256':digest(path),'frames':total_frames,'videos':total_videos},indent=2))
            print(f'IMPORTED {dataset} frames={total_frames} videos={total_videos}',flush=True)
        except (KeyError,FileNotFoundError,ValueError) as error:
            print(f'IMPORT_PENDING {dataset}: {error}',flush=True)
    return {name: ready(name) for name in SPECS}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--watch',action='store_true')
    args=parser.parse_args()
    while True:
        try:
            ready=import_once()
            print(json.dumps(ready),flush=True)
            if all(ready.values()):
                break
        except Exception as error:
            print(f'IMPORT_ERROR {type(error).__name__}: {error}',flush=True)
            if not args.watch:
                raise
        if not args.watch:
            break
        time.sleep(60)


if __name__=='__main__':
    main()
