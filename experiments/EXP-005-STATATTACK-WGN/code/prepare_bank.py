"""Restore a deterministic train-only Real bank from already verified FF++ tars."""
import argparse
from collections import defaultdict
import random
from pathlib import Path

from PIL import Image
from common import REPO,read,write,sha
from restore_lab_data import frame_paths,extract_selected


def main():
 p=argparse.ArgumentParser();p.add_argument('--exp04',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True)
 a=p.parse_args();original=a.exp04.resolve();runtime=a.runtime.resolve()
 manifest=original/'data/FaceForensics++-official.json'
 groups=read(manifest)['FaceForensics++']['FF-real']
 videos=sorted(groups['train']['c23'])
 assert len(videos)==720
 validation=set(groups['val']['c23']);testing=set(groups['test']['c23'])
 assert not set(videos)&(validation|testing)
 rng=random.Random(1024);rng.shuffle(videos)
 paths={video:list(frame_paths(groups['train']['c23'][video])) for video in videos}
 for frames in paths.values():rng.shuffle(frames)
 selected=[]
 for level in range(max(map(len,paths.values()))):
  for video in videos:
   if len(paths[video])>level:selected.append(dict(path=paths[video][level],video=video,label=0))
   if len(selected)==960:break
  if len(selected)==960:break
 assert len({r['path'] for r in selected})==960
 state={'seed':1024,'source':'FF++ c23 train Real only','selection':'video round-robin; deterministic shuffled videos/frames',
        'manifest_sha256':sha(manifest),'records':selected,'train_videos':len(videos),'complete':False}
 output=runtime/'reference-bank.json'
 if output.exists():
  before=read(output)
  assert [{k:r[k] for k in ('path','video','label')} for r in before['records']]==selected
  assert before['manifest_sha256']==state['manifest_sha256']
 checks={line.split(maxsplit=1)[1].strip():line.split()[0]
         for line in (original/'data-archives/SHA256SUMS.txt').read_text().splitlines()}
 wanted={r['path'] for r in selected};verified=[];copied=0
 for remote,digest in checks.items():
  if not remote.startswith('shards/ffpp/'):continue
  archive=original/'data-archives'/remote
  if not archive.is_file() or sha(archive)!=digest:raise ValueError('Missing/unverified bank archive: '+remote)
  copied+=extract_selected(archive,runtime/'reference-data',wanted)
  verified.append(dict(path=remote,sha256=digest))
 assert copied==960
 for record in selected:
  path=runtime/'reference-data'/record['path']
  with Image.open(path) as image:
   image.load();assert image.mode=='RGB' and image.size==(256,256)
  record['image_sha256']=sha(path)
 state['verified_shards']=verified;state['complete']=True;write(output,state)
 print('REFERENCE_BANK_READY',output,flush=True)


if __name__=='__main__':main()
