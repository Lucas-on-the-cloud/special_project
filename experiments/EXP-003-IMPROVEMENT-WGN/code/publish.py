"""Package final experiment handoff artifacts, commit them, and verify GitHub."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
RUNS = Path('C:/sp/runs/wgn_overnight')
EXP3 = REPO / 'experiments' / 'EXP-003-IMPROVEMENT-WGN'
GIT = Path('C:/sp/.tools/git-portable/cmd/git.exe')
BRANCH = 'main'
PORTABLE_FILES = [
    'best.pt', 'summary.json', 'resolved_config.yaml', 'environment.json',
    'metrics.jsonl', 'progress.json', 'source.patch', 'difficulty.json',
    'evaluation.json', 'evaluation-celebdf-official-direct.json',
    'cross_manipulation.json',
]


def git(*arguments, timeout=600):
    environment = os.environ.copy()
    environment.update(GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    result = subprocess.run(
        [str(GIT), '-c', 'safe.directory=C:/sp/special_project',
         '-c', 'user.name=Codex', '-c', 'user.email=codex@openai.com',
         '-C', str(REPO), *arguments], text=True, capture_output=True,
        env=environment, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'git {arguments[0]} failed: {result.stderr[-2000:]}')
    return result.stdout.strip()


def sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def target_for(run):
    if run.name == 'baseline_final':
        return REPO / 'experiments' / 'EXP-002-WGN' / 'reproduction' / 'artifacts' / run.name
    return EXP3 / 'artifacts' / run.name


def concatenate_logs(paths, destination):
    available = [path for path in paths if path.exists()]
    if not available:
        return
    parts = []
    for path in available:
        parts += [f'===== {path.name} =====\n', path.read_text(encoding='utf-8', errors='replace').rstrip(), '\n\n']
    destination.write_text(''.join(parts).rstrip() + '\n', encoding='utf-8')


def write_readme(target, run, summary, environment, checkpoint_sha):
    method = summary.get('method', environment.get('method', 'unknown'))
    lines = [
        f'# {run.name}', '',
        'Portable final-run package for EXP-003. This directory contains the '
        'minimum state needed to understand the run and use its selected model on another machine.', '',
        '| Field | Value |', '|---|---|',
        f'| Method | `{method}` |',
        f'| Completed epochs | {summary.get("completed_epochs", "unknown")} |',
        f'| Best epoch | {summary.get("best_epoch", "unknown")} |',
        f'| Selection metric | validation accuracy |',
        f'| GPU | {environment.get("gpu", "unknown")} |',
        f'| Precision | {environment.get("precision", "unknown")} |',
        f'| Training source commit | `{environment.get("git_commit", "unknown")}` |',
        f'| Training manifest SHA-256 | `{environment.get("manifest_sha256", summary.get("manifest_sha256", "unknown"))}` |',
        f'| Checkpoint SHA-256 | `{checkpoint_sha}` |', '',
        'Use `best.pt` for inference and final evaluation. `last.pt` is intentionally '
        'not committed to normal Git history because it contains optimizer state and '
        'would create large repeated blobs; use a GitHub Release asset when an unfinished '
        'run must be moved and resumed.', '',
        'Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. '
        '`training.log` records the executed training command and epoch output; '
        '`evaluation.log` collects the available locked-evaluation logs. '
        '`ARTIFACT-MANIFEST.json` inventories the package and its checksums.', '',
        'Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`]'
        '(../../../../docs/experiment-backup-and-machine-handoff.md).',
    ]
    (target / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_checksums_and_manifest(target, run, summary, environment, checkpoint_sha):
    excluded = {'SHA256SUMS.txt', 'ARTIFACT-MANIFEST.json'}
    payload_files = sorted(path for path in target.iterdir() if path.is_file() and path.name not in excluded)
    checksums = [f'{sha256(path)}  {path.name}' for path in payload_files]
    (target / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8')
    inventoried = sorted(path for path in target.iterdir()
                         if path.is_file() and path.name != 'ARTIFACT-MANIFEST.json')
    manifest = {
        'schema_version': 1,
        'experiment': 'EXP-002-WGN' if run.name == 'baseline_final' else 'EXP-003-IMPROVEMENT-WGN',
        'run_name': run.name,
        'method': summary.get('method'),
        'status': 'complete',
        'completed_epochs': summary.get('completed_epochs'),
        'best_epoch': summary.get('best_epoch'),
        'checkpoint_sha256': checkpoint_sha,
        'training_git_commit': environment.get('git_commit'),
        'training_manifest_sha256': environment.get('manifest_sha256', summary.get('manifest_sha256')),
        'runtime_path': str(run),
        'files': [{'name': path.name, 'bytes': path.stat().st_size, 'sha256': sha256(path)}
                  for path in inventoried],
    }
    (target / 'ARTIFACT-MANIFEST.json').write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return manifest


def package_run(run):
    run = Path(run)
    if not (run / 'summary.json').exists() or not (run / 'best.pt').exists():
        raise FileNotFoundError(f'Publish requires a complete training run and best.pt: {run}')
    summary = json.loads((run / 'summary.json').read_text())
    if summary['pilot']:
        raise ValueError('Pilot checkpoints are not published as final artifacts')
    source = run / 'best.pt'
    if source.stat().st_size > 95 * 1024**2:
        raise ValueError('Checkpoint exceeds direct GitHub blob budget; use a Release or Git LFS')
    target = target_for(run)
    target.mkdir(parents=True, exist_ok=True)
    for name in PORTABLE_FILES:
        if (run / name).exists():
            shutil.copy2(run / name, target / name)
    training_log = RUNS / 'logs' / f'{run.name}.log'
    if training_log.exists():
        shutil.copy2(training_log, target / 'training.log')
    method = summary.get('method', run.name.removesuffix('_final'))
    concatenate_logs([
        RUNS / 'logs' / f'early_evaluate_{method}.log',
        RUNS / 'logs' / f'evaluate_celebdf_official_{method}.log',
        RUNS / 'logs' / f'evaluate_{method}.log',
    ], target / 'evaluation.log')
    environment = json.loads((run / 'environment.json').read_text())
    checkpoint_sha = sha256(source)
    write_readme(target, run, summary, environment, checkpoint_sha)
    manifest = write_checksums_and_manifest(target, run, summary, environment, checkpoint_sha)
    return target, manifest


def generate_registry():
    rows = []
    for path in sorted((EXP3 / 'artifacts').glob('*/ARTIFACT-MANIFEST.json')):
        value = json.loads(path.read_text())
        rows.append({key: value.get(key) for key in [
            'run_name', 'method', 'status', 'completed_epochs', 'best_epoch',
            'checkpoint_sha256', 'training_git_commit', 'training_manifest_sha256']})
        rows[-1]['artifact_path'] = path.parent.relative_to(REPO).as_posix()
    registry = {'schema_version': 1, 'experiment': 'EXP-003-IMPROVEMENT-WGN', 'runs': rows}
    destination = EXP3 / 'results' / 'EXPERIMENT-REGISTRY.json'
    destination.write_text(json.dumps(registry, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    lines = ['# EXP-003 experiment registry', '',
             '| Run | Method | Epochs | Best epoch | Checkpoint SHA-256 |',
             '|---|---|---:|---:|---|']
    for row in rows:
        lines.append(f"| [{row['run_name']}](../artifacts/{row['run_name']}/) | {row['method']} | "
                     f"{row['completed_epochs']} | {row['best_epoch']} | `{row['checkpoint_sha256']}` |")
    lines += ['', 'Machine-readable registry: [`EXPERIMENT-REGISTRY.json`](EXPERIMENT-REGISTRY.json).', '']
    (EXP3 / 'results' / 'EXPERIMENT-REGISTRY.md').write_text('\n'.join(lines), encoding='utf-8')
    return destination


def commit_and_push(packages, message):
    from report import generate
    generate()
    overview = EXP3 / 'results' / 'RESULTS.md'
    shutil.copy2(RUNS / 'RESULTS.md', overview)
    registry = generate_registry()
    for target, _ in packages:
        git('add', '-f', '--', target.relative_to(REPO).as_posix())
    git('add', '--', overview.relative_to(REPO).as_posix(), registry.relative_to(REPO).as_posix(),
        (EXP3 / 'results' / 'EXPERIMENT-REGISTRY.md').relative_to(REPO).as_posix())
    if git('diff', '--cached', '--name-only'):
        git('commit', '-m', message)
    commit = git('rev-parse', 'HEAD')
    git('push', 'origin', f'HEAD:refs/heads/{BRANCH}')
    remote = git('ls-remote', 'origin', f'refs/heads/{BRANCH}').split()[0]
    if remote != commit:
        raise RuntimeError('Remote commit verification failed')
    for target, manifest in packages:
        relative = target.relative_to(REPO).as_posix()
        source = Path(manifest['runtime_path']) / 'best.pt'
        if git('rev-parse', f'HEAD:{relative}/best.pt') != git('hash-object', str(source)):
            raise RuntimeError(f'Committed checkpoint differs from local best.pt: {source}')
        status = {'status': 'uploaded', 'commit': commit,
                  'checkpoint_sha256': manifest['checkpoint_sha256'],
                  'url': f'https://github.com/Lucas-on-the-cloud/special_project/tree/{BRANCH}/{relative}'}
        (source.parent / 'github-upload.json').write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps({'status': 'uploaded', 'commit': commit,
                      'runs': [manifest['run_name'] for _, manifest in packages]}), flush=True)
    return commit


def publish_runs(runs, message):
    if git('branch', '--show-current') != BRANCH:
        raise RuntimeError(f'Artifact upload requires branch {BRANCH}')
    packages = [package_run(run) for run in runs]
    return commit_and_push(packages, message)


def publish_run(run):
    run = Path(run)
    return publish_runs([run], f'Save WGN {run.name} checkpoint and experiment handoff')


def backfill_exp003():
    runs = []
    for run in sorted(RUNS.glob('*_final')):
        summary = run / 'summary.json'
        if run.name == 'baseline_final' or not summary.exists() or not (run / 'best.pt').exists():
            continue
        if not json.loads(summary.read_text()).get('pilot', True):
            runs.append(run)
    if not runs:
        raise FileNotFoundError('No completed EXP-003 final runs found')
    return publish_runs(runs, 'Backfill portable EXP-003 experiment handoffs')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--run')
    group.add_argument('--backfill-exp003', action='store_true')
    args = parser.parse_args()
    backfill_exp003() if args.backfill_exp003 else publish_run(args.run)
