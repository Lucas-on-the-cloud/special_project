from __future__ import annotations

import argparse
from collections import defaultdict
import copy
import json
import importlib.metadata
import math
import os
from pathlib import Path
import platform
import random
import subprocess
import time

import common
import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader, Subset
import yaml

from common import ROOT, atomic_json, atomic_save, config_load, make_model, seed_all, sha256
from data import (DegradationPairDataset, PairedDataset, build_datasets,
                  curriculum_indices, external_datasets, fraction_for_epoch)
from wgn.data import FaceForensicsJsonDataset, seed_worker


def loader(dataset, config, training=False, epoch=0):
    return DataLoader(dataset, batch_size=config['training']['micro_batch_size'], shuffle=training,
                      num_workers=config['training']['workers'], pin_memory=True,
                      drop_last=training, worker_init_fn=seed_worker,
                      generator=torch.Generator().manual_seed(config['seed'] + epoch),
                      persistent_workers=False)


def metrics(labels, probabilities):
    if len(set(labels)) != 2:
        raise ValueError('Both classes are required for AUC')
    if not np.isfinite(probabilities).all():
        raise FloatingPointError('Non-finite prediction')
    return {'accuracy': float(accuracy_score(labels, np.asarray(probabilities) >= .5)),
            'auc': float(roc_auc_score(labels, probabilities))}


@torch.no_grad()
def evaluate(model, batches):
    model.eval()
    labels, scores = [], []
    video_scores, video_labels = defaultdict(list), {}
    loss_sum, count = 0., 0
    for batch in batches:
        targets = batch['label'].cuda(non_blocking=True)
        logits = model(batch['image'].cuda(non_blocking=True))
        loss_sum += float(F.binary_cross_entropy_with_logits(logits, targets, reduction='sum'))
        count += len(targets)
        probabilities = logits.sigmoid().cpu().tolist()
        batch_labels = targets.cpu().tolist()
        labels.extend(batch_labels)
        scores.extend(probabilities)
        for group, video, label, probability in zip(batch['manipulation'], batch['video'], batch_labels, probabilities):
            key = (group, video)
            if key in video_labels and video_labels[key] != label:
                raise ValueError(f'Conflicting labels for video {key}')
            video_labels[key] = label
            video_scores[key].append(probability)
    if not count:
        raise ValueError('Empty evaluation dataset')
    ordered = sorted(video_scores)
    return {'loss': loss_sum/count, 'frames': count, 'videos': len(ordered), **metrics(labels, scores),
            **{'video_'+key: value for key, value in metrics([video_labels[k] for k in ordered],
                                                [float(np.mean(video_scores[k])) for k in ordered]).items()}}


def loss_for_batch(model, batch, consistency_lambda=0.):
    images = batch['image'].cuda(non_blocking=True)
    targets = batch['label'].cuda(non_blocking=True)
    logits = model(images)
    loss = F.binary_cross_entropy_with_logits(logits, targets)
    consistency = torch.zeros((), device='cuda')
    if 'image_pair' in batch:
        pair_logits = model(batch['image_pair'].cuda(non_blocking=True))
        consistency = F.mse_loss(logits.sigmoid(), pair_logits.sigmoid())
        loss = loss + F.binary_cross_entropy_with_logits(pair_logits, targets) + consistency_lambda * consistency
    if not torch.isfinite(loss):
        raise FloatingPointError('Non-finite training loss')
    return loss, logits, consistency


def train_epoch(model, batches, optimizer, config, epoch, max_steps=None):
    model.train()
    accumulation = config['training']['effective_batch_size'] // config['training']['micro_batch_size']
    available_steps = min(len(batches), max_steps) if max_steps else len(batches)
    if not available_steps:
        raise ValueError('Training dataset is smaller than the micro batch')
    optimizer.zero_grad(set_to_none=True)
    labels, scores = [], []
    loss_sum, consistency_sum, count, updates = 0., 0., 0, 0
    started = time.monotonic()
    for step, batch in enumerate(batches):
        if step >= available_steps:
            break
        group_start = (step // accumulation) * accumulation
        divisor = min(accumulation, available_steps - group_start)
        consistency_lambda = config.get('consistency_lambda', config.get('temporal_lambda', 0.))
        loss, logits, consistency = loss_for_batch(model, batch, consistency_lambda)
        (loss/divisor).backward()
        if (step+1) % accumulation == 0 or step+1 == available_steps:
            # Aggregate on GPU and synchronize once, rather than once per parameter.
            norm = torch.linalg.vector_norm(torch.stack([
                parameter.grad.detach().norm() for parameter in model.parameters()
                if parameter.grad is not None]))
            if not torch.isfinite(norm):
                raise FloatingPointError('Non-finite gradient')
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)
            updates += 1
        size = len(batch['label'])
        loss_sum += loss.item()*size
        consistency_sum += consistency.item()*size
        count += size
        labels.extend(batch['label'].tolist())
        scores.extend(logits.detach().sigmoid().cpu().tolist())
        if step % 100 == 0:
            print(json.dumps({'event': 'progress', 'epoch': epoch+1, 'batch': step+1,
                              'batches': available_steps, 'loss': loss.item()}), flush=True)
    torch.cuda.synchronize()
    return {'loss': loss_sum/count, 'consistency': consistency_sum/count, 'samples': count,
            'updates': updates, 'seconds': time.monotonic()-started, **metrics(labels, scores)}


@torch.no_grad()
def difficulty_ranking(config, records, output):
    checkpoint_path = Path(config['curriculum_checkpoint'])
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f'Baseline control checkpoint required: {checkpoint_path}')
    identity = {'checkpoint_sha256': sha256(checkpoint_path),
                'manifest_sha256': sha256(config['data']['json']),
                'paths': [str(record.path) for record in records]}
    cache = output / 'difficulty.json'
    if cache.exists():
        payload = json.loads(cache.read_text())
        if payload['identity'] == identity:
            return payload['losses']
    baseline_config = dict(config, method='baseline')
    baseline = make_model(baseline_config, pretrained=False).cuda().eval()
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    baseline.load_state_dict(checkpoint['model'], strict=True)
    baseline = baseline.cuda().eval()
    losses = []
    dataset = FaceForensicsJsonDataset(records, train=False)
    for batch in loader(dataset, config):
        logits = baseline(batch['image'].cuda(non_blocking=True))
        losses.extend(F.binary_cross_entropy_with_logits(logits, batch['label'].cuda(), reduction='none').cpu().tolist())
    if len(losses) != len(records) or not np.isfinite(losses).all():
        raise ValueError('Invalid training-only difficulty ranking')
    atomic_json(cache, {'identity': identity, 'losses': losses})
    del baseline, checkpoint
    torch.cuda.empty_cache()
    return losses


def checkpoint_payload(model, optimizer, scheduler, config, epoch, best_accuracy, best_epoch, best_val):
    return {'model': model.state_dict(), 'optimizer': optimizer.state_dict(), 'scheduler': scheduler.state_dict(),
            'config': config, 'epoch': epoch, 'best_accuracy': best_accuracy,
            'best_epoch': best_epoch, 'best_val': best_val,
            'rng': {'python': random.getstate(), 'numpy': np.random.get_state(),
                    'torch': torch.get_rng_state(), 'cuda': torch.cuda.get_rng_state_all()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--epochs', type=int)
    parser.add_argument('--pilot', action='store_true', help='Never evaluate test sets in a pilot')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--max-train-steps', type=int)
    args = parser.parse_args()
    config = config_load(args.config)
    if args.epochs:
        config['training']['epochs'] = args.epochs
    config['pilot'] = args.pilot
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'metrics.jsonl').exists() and not args.resume:
        raise FileExistsError('Existing run: pass --resume or use a new output directory')
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required; CPU training is disabled')
    seed_all(config['seed'])
    torch.set_num_threads(config['training'].get('cpu_threads', 4))
    micro, effective = config['training']['micro_batch_size'], config['training']['effective_batch_size']
    if effective % micro or effective < micro:
        raise ValueError('effective_batch_size must be divisible by micro_batch_size')
    manifest_hash = sha256(config['data']['json'])
    train, val, test = build_datasets(config)
    ranking = difficulty_ranking(config, train.records, output) if config['method'] == 'curriculum' else None
    seed_all(config['seed'])  # Difficulty scoring must not change model initialization.
    model = make_model(config).cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=config['training']['learning_rate'],
                                 weight_decay=config['training']['weight_decay'])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config['training']['epochs'])
    start_epoch, best_accuracy, best_epoch, best_val = 0, -1., None, None
    last_path = output / 'last.pt'
    if args.resume and not last_path.exists() and (output/'metrics.jsonl').exists():
        (output/'metrics.jsonl').write_text('')
    if args.resume and last_path.exists():
        checkpoint = torch.load(last_path, map_location='cpu', weights_only=False)
        if checkpoint['config'] != config:
            raise ValueError('Cannot resume with a changed configuration')
        metadata = json.loads((output / 'environment.json').read_text())
        if metadata['manifest_sha256'] != manifest_hash:
            raise ValueError('Cannot resume with a changed dataset manifest')
        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        scheduler.load_state_dict(checkpoint['scheduler'])
        start_epoch = checkpoint['epoch']+1
        best_accuracy, best_epoch, best_val = checkpoint['best_accuracy'], checkpoint['best_epoch'], checkpoint['best_val']
        state = checkpoint['rng']
        random.setstate(state['python'])
        np.random.set_state(state['numpy'])
        torch.set_rng_state(state['torch'])
        torch.cuda.set_rng_state_all(state['cuda'])
        del checkpoint
        # Remove an uncommitted metric record after interruption between metric and checkpoint writes.
        history = output / 'metrics.jsonl'
        if history.exists():
            committed = [json.loads(line) for line in history.read_text().splitlines() if line.strip()]
            history.write_text(''.join(json.dumps(item)+'\n' for item in committed if item['epoch'] < start_epoch))
    output.joinpath('resolved_config.yaml').write_text(yaml.safe_dump(config, sort_keys=False))
    environment = {'python': platform.python_version(), 'torch': torch.__version__, 'cuda': torch.version.cuda,
                   'gpu': torch.cuda.get_device_name(), 'manifest_sha256': manifest_hash,
                   'method': config['method'], 'precision': 'fp32',
                   'micro_batch_size': micro, 'effective_batch_size': effective,
                   'platform': platform.platform(),
                   'packages': {name: importlib.metadata.version(name) for name in [
                       'torch','torchvision','timm','numpy','scikit-learn','Pillow','PyYAML']}}
    git = Path('C:/sp/.tools/git-portable/cmd/git.exe')
    if git.exists():
        environment['git_commit'] = subprocess.check_output([str(git), '-c', 'safe.directory=C:/sp/special_project',
                                 '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
        diff = subprocess.check_output([str(git), '-c', 'safe.directory=C:/sp/special_project',
                                       '-C', str(ROOT), 'diff', '--binary'], text=True)
        (output/'source.patch').write_text(diff, encoding='utf-8')
    atomic_json(output/'environment.json', environment)
    source_snapshot = output/'source'
    source_snapshot.mkdir(exist_ok=True)
    import shutil
    for source in ROOT.glob('*.py'):
        shutil.copy2(source, source_snapshot/source.name)
    started = time.monotonic()
    for epoch in range(start_epoch, config['training']['epochs']):
        seed_all(config['seed'] + epoch)
        fraction = fraction_for_epoch(epoch) if ranking is not None else 1.
        dataset = Subset(train, curriculum_indices(ranking, train.records, fraction)) if ranking is not None else train
        if config['method'] in ('temporal', 'temporal_control'):
            dataset = PairedDataset(train)
        elif config['method'] in ('degradation_control', 'degradation_consistency'):
            dataset = DegradationPairDataset(train, config)
        training = train_epoch(model, loader(dataset, config, True, epoch), optimizer, config, epoch, args.max_train_steps)
        validation = evaluate(model, loader(val, config))
        scheduler.step()
        improved = validation['accuracy'] > best_accuracy
        if improved:
            best_accuracy, best_epoch, best_val = validation['accuracy'], epoch, validation
            atomic_save(output/'best.pt', {'model': model.state_dict(), 'config': config, 'epoch': epoch, 'val': validation})
        record = {'epoch': epoch, 'curriculum_fraction': fraction, 'train': training, 'val': validation,
                  'lr': optimizer.param_groups[0]['lr']}
        with (output/'metrics.jsonl').open('a') as handle:
            handle.write(json.dumps(record, allow_nan=False)+'\n')
        atomic_save(last_path, checkpoint_payload(model, optimizer, scheduler, config, epoch,
                                                 best_accuracy, best_epoch, best_val))
        atomic_json(output/'progress.json', {'status': 'training', 'completed_epochs': epoch+1,
                    'total_epochs': config['training']['epochs'], 'best_epoch': best_epoch+1,
                    'last': record, 'remaining_training_hours_estimate': training['seconds'] *
                    (config['training']['epochs']-epoch-1)/3600})
        print(json.dumps(record, allow_nan=False), flush=True)
    summary = {'method': config['method'], 'pilot': args.pilot, 'best_epoch': best_epoch+1,
               'best_val': best_val, 'checkpoint': str(output/'best.pt'),
               'completed_epochs': config['training']['epochs'], 'manifest_sha256': manifest_hash,
               'wall_seconds_this_invocation': time.monotonic()-started}
    # Final evaluation is a separate queue phase after all candidates have been fixed.
    atomic_json(output/'summary.json', summary)
    atomic_json(output/'progress.json', dict(summary, status='complete'))
    print('TRAINING_COMPLETE '+json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
