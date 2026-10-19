"""Persist the user's requested inference checkpoints and results to GitHub."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
GIT=Path('C:/sp/.tools/git-portable/cmd/git.exe')
BRANCH='main'


def git(*arguments, timeout=600):
    environment=os.environ.copy()
    environment.update(GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
    result=subprocess.run([str(GIT),'-c','safe.directory=C:/sp/special_project',
                '-c','user.name=Codex','-c','user.email=codex@openai.com',
                '-C',str(REPO),*arguments],text=True,capture_output=True,env=environment,timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'git {arguments[0]} failed: {result.stderr[-1000:]}')
    return result.stdout.strip()


def publish_run(run):
    run=Path(run)
    if not (run/'summary.json').exists() or not (run/'best.pt').exists():
        raise FileNotFoundError('Publish requires a complete training run and best.pt')
    summary=json.loads((run/'summary.json').read_text())
    if summary['pilot']:
        raise ValueError('Pilot checkpoints are not published as final artifacts')
    if git('branch','--show-current') != BRANCH:
        raise RuntimeError(f'Checkpoint upload requires branch {BRANCH}')
    if run.name == 'baseline_final':
        target=REPO/'experiments'/'EXP-002-WGN'/'reproduction'/'artifacts'/run.name
    else:
        target=REPO/'experiments'/'EXP-003-IMPROVEMENT-WGN'/'artifacts'/run.name
    target.mkdir(parents=True,exist_ok=True)
    source=run/'best.pt'
    if source.stat().st_size > 95*1024**2:
        raise ValueError('Checkpoint exceeds direct GitHub blob budget; use a Release/LFS')
    names=['best.pt','summary.json','resolved_config.yaml','environment.json','metrics.jsonl','evaluation.json',
           'evaluation-celebdf-official-direct.json','cross_manipulation.json']
    for name in names:
        if (run/name).exists():
            shutil.copy2(run/name,target/name)
    with source.open('rb') as handle:
        digest=hashlib.file_digest(handle,'sha256').hexdigest()
    (target/'SHA256SUMS.txt').write_text(f'{digest}  best.pt\n')
    from report import generate
    generate()
    overview=REPO/'experiments'/'EXP-003-IMPROVEMENT-WGN'/'results'/'RESULTS.md'
    shutil.copy2(Path('C:/sp/runs/wgn_overnight/RESULTS.md'),overview)
    relative=target.relative_to(REPO).as_posix()
    git('add','-f','--',relative)
    git('add','--',overview.relative_to(REPO).as_posix())
    if git('diff','--cached','--name-only'):
        git('commit','-m',f'Save WGN {run.name} checkpoint and experiment results')
    commit=git('rev-parse','HEAD')
    git('push','origin',f'HEAD:refs/heads/{BRANCH}')
    remote=git('ls-remote','origin',f'refs/heads/{BRANCH}').split()[0]
    if remote != commit:
        raise RuntimeError('Remote commit verification failed')
    # Verify that the committed checkpoint is exactly the local checkpoint.
    blob=git('rev-parse',f'HEAD:{relative}/best.pt')
    if blob != git('hash-object',str(source)):
        raise RuntimeError('Committed checkpoint blob differs from local best.pt')
    status={'status':'uploaded','commit':commit,'checkpoint_sha256':digest,
            'url':f'https://github.com/Lucas-on-the-cloud/special_project/blob/{BRANCH}/{relative}/best.pt'}
    (run/'github-upload.json').write_text(json.dumps(status,indent=2))
    print(json.dumps(status),flush=True)
    return status


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',required=True)
    publish_run(parser.parse_args().run)
