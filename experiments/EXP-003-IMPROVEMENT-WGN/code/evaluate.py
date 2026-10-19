from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

import common
import torch
from common import atomic_json, config_load, make_model, sha256
from data import build_datasets, external_datasets
from preflight import inspect
from train import evaluate, loader


def evaluate_run(run, config_path):
    run=Path(run)
    config=config_load(config_path)
    if not (run/'summary.json').exists():
        raise FileNotFoundError('Final training must finish before locked evaluation')
    if json.loads((run/'summary.json').read_text())['pilot']:
        raise ValueError('Pilots cannot evaluate locked targets')
    output=run/'evaluation.json'
    result=json.loads(output.read_text()) if output.exists() else {}
    checkpoint_sha=sha256(run/'best.pt')
    if result and result['checkpoint_sha256'] != checkpoint_sha:
        raise ValueError('Refusing to overwrite evaluation for a different checkpoint')
    result.setdefault('checkpoint_sha256',checkpoint_sha)
    result.setdefault('datasets',{})
    result.setdefault('pending',[])
    model=make_model(config,pretrained=False).cuda().eval()
    model.load_state_dict(torch.load(run/'best.pt',map_location='cpu',weights_only=False)['model'])

    def run_target(name,dataset,manifest_path):
        # Adding c40/FaceShifter to the shared JSON does not change the c23 test set.
        identity=hashlib.sha256(json.dumps([(str(r.path),r.label,r.manipulation,r.video)
                                           for r in dataset.records]).encode()).hexdigest()
        if name in result['datasets']:
            if result['datasets'][name]['manifest_sha256'] != identity:
                raise ValueError(f'Evaluation dataset changed after locked test: {name}')
            return
        inspect(dataset,name,full_decode=False)
        measured=evaluate(model,loader(dataset,config))
        result['datasets'][name]={'manifest_sha256':identity,**measured}
        atomic_json(output,result)
        print(f'EVALUATED {name} '+json.dumps(measured),flush=True)

    _,_,test=build_datasets(config)
    run_target('FF++ c23',test,config['data']['json'])
    pending=[]
    for target in config.get('external',[]):
        if not Path(target['json']).exists():
            pending.append(target['dataset'])
            continue
        local=dict(config,external=[target])
        name,dataset=next(external_datasets(local))
        run_target(name,dataset,target['json'])
    c40=json.loads(Path(config['data']['json']).read_text())['FaceForensics++']
    if all('c40' in c40[group]['test'] and c40[group]['test']['c40'] for group in ['FF-real','FF-DF','FF-F2F','FF-FS','FF-NT']):
        import copy
        control=copy.deepcopy(config)
        control['data']['compression']='c40'
        _,_,test=build_datasets(control)
        run_target('FF++ c40',test,config['data']['json'])
    else:
        pending.append('FF++ c40')
    for compression in ['c23','c40']:
        name=f'FaceShifter {compression} (held-out)'
        if not c40.get('FF-FSh',{}).get('test',{}).get(compression):
            pending.append(name)
            continue
        import copy
        target=copy.deepcopy(config)
        target['data'].update(compression=compression,manipulations=['FF-FSh'])
        _,_,test=build_datasets(target)
        run_target(name,test,config['data']['json'])
    result['pending']=pending
    atomic_json(output,result)
    del model
    torch.cuda.empty_cache()
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',required=True)
    parser.add_argument('--config',required=True)
    args=parser.parse_args()
    evaluate_run(args.run,args.config)
