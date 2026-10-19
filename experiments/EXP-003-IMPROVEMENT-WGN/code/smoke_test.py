"""Real CUDA forward/backward, optimizer, sampler and checkpoint round-trip checks."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import tempfile
import time

import common
import numpy as np
from PIL import Image
import torch

from common import atomic_json, config_load, make_model, seed_all
from data import (DegradationPairDataset, PairedDataset, build_datasets,
                  curriculum_indices, fraction_for_epoch)
from train import loader, loss_for_batch, evaluate


def synthetic_config(config, destination):
    """Synthetic images are solely a code test, never experimental results."""
    result = copy.deepcopy(config)
    result['model']['pretrained'] = False
    result['training']['workers'] = 0
    result['data']['root'] = str(destination)
    result['data']['json'] = str(destination/'synthetic.json')
    result['data']['frames_per_real'] = 4
    result['data']['frames_per_fake'] = 4
    result['data']['manipulations'] = ['FF-DF']
    payload = {'FaceForensics++': {}}
    rng = np.random.default_rng(1024)
    for group in ('FF-real', 'FF-DF'):
        payload['FaceForensics++'][group] = {}
        for split in ('train', 'val', 'test'):
            videos = {}
            for video_index in range(4):
                video = f'{split}_{video_index}'
                paths = []
                for frame in range(4):
                    path = destination/group/video/f'{frame}.png'
                    path.parent.mkdir(parents=True, exist_ok=True)
                    Image.fromarray(rng.integers(0, 256, (256, 256, 3), dtype=np.uint8)).save(path)
                    paths.append(str(path.relative_to(destination)))
                videos[video] = {'frames': paths, 'label': group}
            payload['FaceForensics++'][group][split] = {'c23': videos}
    atomic_json(destination/'synthetic.json', payload)
    return result


def check(config, mode):
    seed_all(config['seed'])
    torch.set_num_threads(4)
    train, val, _ = build_datasets(config)
    model = make_model(config, pretrained=False if mode == 'synthetic' else None).cuda()
    model.train()
    if config['method'] in ('temporal', 'temporal_control'):
        dataset = PairedDataset(train)
    elif config['method'] in ('degradation_control', 'degradation_consistency'):
        dataset = DegradationPairDataset(train, config)
    else:
        dataset = train
    batch = next(iter(loader(dataset, config, training=True)))
    if 'path_pair' in batch:
        if config['method'] in ('temporal', 'temporal_control'):
            assert all(a != b for a, b in zip(batch['path'], batch['path_pair']))
        else:
            assert all(a == b for a, b in zip(batch['path'], batch['path_pair']))
            assert not torch.equal(batch['image'], batch['image_pair'])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)
    before = model.classifier.weight.detach().clone()
    torch.cuda.reset_peak_memory_stats()
    started = time.monotonic()
    for _ in range(2):
        optimizer.zero_grad(set_to_none=True)
        consistency_lambda = config.get('consistency_lambda', config.get('temporal_lambda', 0.))
        loss, logits, consistency = loss_for_batch(model, batch, consistency_lambda)
        assert logits.shape == batch['label'].shape
        loss.backward()
        assert all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None)
        if config['method'] == 'gradient':
            assert model.gradient_projection[0].weight.grad.abs().sum() > 0
            assert model.branch_gate.weight.grad is not None
        optimizer.step()
    assert not torch.equal(before, model.classifier.weight)
    model.eval()
    with torch.no_grad():
        reference = model(batch['image'].cuda())
    with tempfile.TemporaryDirectory(prefix='wgn-checkpoint-') as temporary:
        checkpoint = Path(temporary)/'roundtrip.pt'
        torch.save({'model': model.state_dict()}, checkpoint)
        restored = make_model(config, pretrained=False).cuda().eval()
        restored.load_state_dict(torch.load(checkpoint, map_location='cpu', weights_only=False)['model'])
        with torch.no_grad():
            torch.testing.assert_close(reference, restored(batch['image'].cuda()), rtol=1e-5, atol=1e-6)
        del restored
    assert [fraction_for_epoch(i) for i in (0, 7, 8, 15, 16, 24)] == [.5, .5, .75, .75, 1., 1.]
    ranking = list(range(len(train.records)))
    previous = set()
    for fraction in (.5, .75, 1.):
        selected = set(curriculum_indices(ranking, train.records, fraction))
        assert previous.issubset(selected)
        assert {train.records[i].label for i in selected} == {0, 1}
        previous = selected
    assert len(previous) == len(train)
    # A real validation batch/metric path check, with both classes and grouped video keys.
    val_metrics = evaluate(model, loader(val, config)) if mode == 'synthetic' else None
    torch.cuda.synchronize()
    result = {'status': 'passed', 'method': config['method'], 'mode': mode,
              'loss': loss.item(), 'consistency': consistency.item(),
              'micro_batch_size': config['training']['micro_batch_size'],
              'peak_allocated_GiB': torch.cuda.max_memory_allocated()/1024**3,
              'seconds': time.monotonic()-started, 'validation': val_metrics,
              'gpu': torch.cuda.get_device_name(), 'torch': torch.__version__}
    del model, optimizer, dataset
    torch.cuda.empty_cache()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--synthetic', action='store_true')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    config = config_load(args.config)
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA smoke test requires a usable GPU')
    if args.synthetic:
        with tempfile.TemporaryDirectory(prefix='wgn-synthetic-') as temporary:
            result = check(synthetic_config(config, Path(temporary)), 'synthetic')
    else:
        result = check(config, 'real-data')
    atomic_json(args.output, result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
