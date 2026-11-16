"""Sequential, fail-closed full Celeb-DF-v2 / WildDeepfake evaluation queue.

Requires restore_lab_data.py to restore both groups (it may run concurrently).
Locks full cohorts before inference, gates each clean baseline, then runs the
unchanged four-method protocol followed by audited postprocessing. Re-running
does not overwrite a run directory or pre-existing protocol/cohort locks.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from evaluation_data import cohort_fingerprint, load_records, reference_target
from summarize_final import METHODS, read, sha

DATA = {
    'celebdf': ('celebdf_official_direct','Celeb-DF-v2-official-direct.json'),
    'wilddeepfake': ('wilddeepfake','WildDeepfake.json'),
}


def write(path,value):
    temporary=path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
    temporary.replace(path)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--runtime-root',type=Path,required=True)
    a=p.parse_args()
    repo=a.repo_root.resolve(); runtime=a.runtime_root.resolve()
    code=Path(__file__).resolve().parent
    checkpoint=runtime/'checkpoints/baseline_final/best.pt'
    state={'pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat(),
           'stage':'locking','datasets':{},'complete':False}
    status=runtime/'external-full-status.json'
    template=read(code/'configs/final_reconstruction_dfdc_full.json')
    prior=read(runtime/'runs/final_dfdc_full_reconstruction_001/results.json')['metadata']
    assert sha(checkpoint)==prior['checkpoint_sha256']
    for name in ('jia_faa.py','paper_aligned_attacks.py','diagnostics.py','image_quality.py','run_exp04_v2.py'):
        assert sha(code/name)==prior['source_sha256'][name], name
    for ds,(group,filename) in DATA.items():
        config={**template,'dataset':ds}
        lock=code/'configs'/f'final_reconstruction_{ds}_full.json'
        if lock.exists():
            assert read(lock)==config
        else:
            write(lock,config)
        manifest=runtime/'data'/filename
        records=load_records(repo,manifest,runtime/'data',{},ds)
        reference=reference_target(repo,ds)
        assert len(records)==reference['frames']
        assert cohort_fingerprint(records,runtime/'data',windows_reference=True)==reference['manifest_sha256']
        cohort_path=runtime/'cohorts'/f'full_{ds}.json'
        cohort={'locked_at_utc':datetime.now(timezone.utc).isoformat(),'dataset':ds,
            'seed':config['seed'],'selection':'all records in locked test manifest; no score selection',
            'frames':len(records),'real':sum(r.label==0 for r in records),'fake':sum(r.label==1 for r in records),
            'video_records':len({(r.manipulation,r.video,r.label) for r in records}),
            'cohort_fingerprint':cohort_fingerprint(records,runtime/'data'),
            'checkpoint_sha256':sha(checkpoint),'manifest_sha256':sha(manifest),
            'protocol_lock_sha256':sha(lock),
            'records':[dict(path=r.path.relative_to(runtime/'data').as_posix(),label=r.label,
                            video=r.video,manipulation=r.manipulation) for r in records]}
        if cohort_path.exists():
            before=read(cohort_path)
            assert {k:v for k,v in before.items() if k!='locked_at_utc'}=={k:v for k,v in cohort.items() if k!='locked_at_utc'}
        else:
            write(cohort_path,cohort)
        state['datasets'][ds]={k:cohort[k] for k in ('frames','real','fake','video_records','cohort_fingerprint')}
    write(status,state)

    def run(stage,command,log):
        state['stage']=stage; state['updated_utc']=datetime.now(timezone.utc).isoformat(); write(status,state)
        print('START '+stage,flush=True)
        with log.open('w') as output:
            subprocess.run([sys.executable,'-u',*map(str,command)],stdout=output,stderr=subprocess.STDOUT,check=True)
        print('DONE '+stage,flush=True)

    try:
        for ds,(group,filename) in DATA.items():
            state['stage']='waiting_restoration_'+ds; write(status,state)
            deadline=time.monotonic()+4*3600
            while not read(runtime/'data-restoration.json')['groups'].get(group,{}).get('complete'):
                if time.monotonic()>deadline:
                    raise TimeoutError('Data restoration did not finish: '+group)
                time.sleep(10)
            manifest=runtime/'data'/filename
            clean=runtime/'runs'/f'clean_{ds}.json'
            common=['--repo-root',repo,'--checkpoint',checkpoint,'--manifest',manifest,
                    '--data-root',runtime/'data','--dataset',ds]
            run('clean_'+ds,[code/'validate_clean_reference.py',*common,'--output',clean],
                runtime/'runs'/f'clean_{ds}.log')
            lock=code/'configs'/f'final_reconstruction_{ds}_full.json'
            config=read(lock)
            folder=runtime/'runs'/f'final_{ds}_full_reconstruction_001'
            command=[code/'run_exp04_v3.py',*common,'--output',folder,
                     '--purpose','final','--protocol-lock',lock,'--clean-reference',clean]
            for key,value in config.items():
                if key=='dataset':continue
                command+=['--'+key.replace('_','-')]
                command+=value if isinstance(value,list) else [str(value)]
            run('attack_'+ds,command,folder.with_suffix('.log'))
            for method in METHODS:
                run('analysis_'+ds+'_'+method,[code/'analyze_by_video.py','--run',folder,
                    '--method',method,'--bootstrap','1000'],folder/(method+'_analysis.log'))
            run('audit_'+ds,[code/'summarize_external_full.py','--runtime-root',runtime,
                '--dataset',ds,'--output-dir',code.parent/'results'],runtime/'runs'/f'audit_{ds}_full.log')
            state['datasets'][ds]['complete']=True; write(status,state)
        state['stage']='complete';state['complete']=True
        state['finished_utc']=datetime.now(timezone.utc).isoformat();write(status,state)
        print('EXTERNAL_FULL_QUEUE_COMPLETE',flush=True)
    except BaseException as error:
        state['error']=str(error);state['failed_stage']=state['stage'];state['stage']='failed'
        write(status,state)
        raise


if __name__=='__main__':
    main()
