from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import common
import numpy as np
import torch
from common import atomic_json, config_load, make_model, sha256
from data import build_datasets
from train import evaluate, loader


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    parser.add_argument('--run',required=True)
    args=parser.parse_args()
    run=Path(args.run)
    config=config_load(args.config)
    checkpoint=run/'best.pt'
    output=run/'cross_manipulation.json'
    if output.exists():
        old=json.loads(output.read_text())
        if old['checkpoint_sha256']==sha256(checkpoint):
            print('LOCKED_EVALUATION_ALREADY_COMPLETE',flush=True)
            return
        raise ValueError('Checkpoint changed after locked cross-manipulation evaluation')
    model=make_model(config,pretrained=False).cuda().eval()
    model.load_state_dict(torch.load(checkpoint,map_location='cpu',weights_only=False)['model'])
    values={}
    for group in ['FF-DF','FF-F2F','FF-FS','FF-NT']:
        target=copy.deepcopy(config)
        target['data']['manipulations']=[group]
        _,_,test=build_datasets(target)
        values[group]=evaluate(model,loader(test,target))
    training_group=config['data']['manipulations'][0]
    result={'checkpoint_sha256':sha256(checkpoint),'training_manipulation':training_group,'results':values,
            'average_auc_including_diagonal':float(np.mean([item['auc'] for item in values.values()])),
            'average_unseen_auc':float(np.mean([item['auc'] for key,item in values.items() if key!=training_group]))}
    atomic_json(output,result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
