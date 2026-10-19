"""Validate the actual available external RGB data and a forward pass, without test metrics."""
from __future__ import annotations

import argparse
from pathlib import Path

import common
import torch
from common import atomic_json, config_load, make_model
from data import external_datasets
from preflight import inspect
from train import loader


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    config=config_load(args.config)
    model=make_model(config,pretrained=False).cuda().eval()
    result={'checked':{},'pending':[]}
    for target in config['external']:
        if not Path(target['json']).exists():
            result['pending'].append(target['dataset'])
            continue
        try:
            name,dataset=next(external_datasets(dict(config,external=[target])))
            report=inspect(dataset,name,full_decode=False)
        except (FileNotFoundError,KeyError) as error:
            result['pending'].append({'dataset':target['dataset'],'reason':str(error)})
            continue
        batch=next(iter(loader(dataset,config)))
        with torch.no_grad():
            logits=model(batch['image'].cuda())
            assert torch.isfinite(logits).all()
        result['checked'][name]=dict(report,status='passed')
    if not result['checked']:
        raise ValueError('At least one real external target must pass preflight before final runs')
    atomic_json(args.output,result)
    print(result,flush=True)


if __name__=='__main__':
    main()
