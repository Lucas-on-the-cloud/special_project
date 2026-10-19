"""Short CUDA integration check of the actual trainer, ranking and resume commands."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

import common
import yaml
from common import ROOT, atomic_json, config_load
from smoke_test import synthetic_config

REFERENCE_CONFIG=ROOT.parents[2]/'experiments'/'EXP-002-WGN'/'reproduction'/'code'/'configs'/'wgn_ffpp_c23_rtx5060.yaml'


def main():
    output=Path('C:/sp/runs/wgn_overnight/validation')
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='wgn-integration-') as temporary:
        root=Path(temporary)
        settings=synthetic_config(config_load(REFERENCE_CONFIG),root/'images')
        settings['training'].update(micro_batch_size=8,effective_batch_size=32,workers=2,epochs=1)
        reports={}
        for method in ['baseline','gradient','curriculum','temporal_control','temporal']:
            config=dict(settings,method=method,temporal_lambda=.1 if method=='temporal' else 0.)
            config['curriculum_checkpoint']=str(root/'baseline'/'best.pt')
            config_path=root/f'{method}.yaml'
            config_path.write_text(yaml.safe_dump(config))
            command=[sys.executable,str(ROOT/'train.py'),'--config',str(config_path),
                     '--output-dir',str(root/method),'--max-train-steps','4']
            with (output/f'{method}.log').open('w') as log:
                subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
                subprocess.run(command+['--resume'],stdout=log,stderr=subprocess.STDOUT,check=True)
            summary=json.loads((root/method/'summary.json').read_text())
            history=(root/method/'metrics.jsonl').read_text().splitlines()
            assert len(history)==1, 'Resume must not duplicate completed epochs'
            assert summary['completed_epochs']==1
            if method=='curriculum':
                ranking=json.loads((root/method/'difficulty.json').read_text())
                assert len(ranking['losses'])==32
            reports[method]={'status':'passed','steps':json.loads(history[0])['train']['updates'],
                             'checkpoint_roundtrip_and_resume':True}
            print(f'INTEGRATION_PASSED {method}',flush=True)
        atomic_json(output/'integration.json',reports)


if __name__=='__main__':
    main()
