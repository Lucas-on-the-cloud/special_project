"""Authorized EXP-005 queue, waiting for successful EXP-004 completion."""
import argparse
import fcntl
from datetime import datetime,timezone
import os
from pathlib import Path
import subprocess
import sys
import time

from common import *


def main():
 p=argparse.ArgumentParser()
 for key in ('exp04','runtime','profile'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();exp04=a.exp04.resolve();runtime=a.runtime.resolve()
 queue_lock=(runtime/'queue.lock').open('a')
 fcntl.flock(queue_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 status=runtime/'queue-status.json';ready=read(runtime/'ready.json')
 state={'pid':os.getpid(),'stage':'waiting_exp04','started_utc':datetime.now(timezone.utc).isoformat(),
        'complete':False,'datasets':{k:{'complete':False} for k in DATASETS},
        'profile_sha256':sha(a.profile),'predecessor_status':str(exp04/'external-full-status.json')}
 write(status,state)

 def verify_ready():
  assert ready['cpu_tests_passed'] and ready['source_sha256']==source_hashes(),'Readiness/source mismatch'
  assert ready['cpu_tests_xml_sha256']==sha(runtime/'cpu-tests.xml')
  assert ready['profile_sha256']==sha(a.profile)
  assert read(a.profile)['algorithm_spec_sha256']==sha(CODE.parent/'docs/HOU-ALGORITHM-SPEC.md')
  assert ready['reference_bank_sha256']==sha(runtime/'reference-bank.json')
  assert read(runtime/'reference-bank.json')['complete']

 def run(stage,command,log):
  state['stage']=stage;state['updated_utc']=datetime.now(timezone.utc).isoformat();write(status,state)
  print('START '+stage,flush=True)
  with log.open('a') as stream:
   subprocess.run([sys.executable,'-u',*map(str,command)],stdout=stream,stderr=subprocess.STDOUT,check=True)
  print('DONE '+stage,flush=True)

 try:
  verify_ready()
  while True:
   prior=read(exp04/'external-full-status.json')
   if prior.get('stage')=='failed':raise RuntimeError('EXP-004 failed; not starting EXP-005')
   if prior.get('complete'):
    assert all(v.get('complete') for v in prior['datasets'].values())
    for dataset,(_,run_name,_,_) in DATASETS.items():assert read(exp04/'runs'/run_name/'results.json')['complete']
    break
   time.sleep(10)
  verify_ready()
  (runtime/'clean').mkdir(exist_ok=True)
  for ds,(filename,_,_,_) in DATASETS.items():
   run('clean_'+ds,[SHARED/'validate_clean_reference.py','--repo-root',REPO,
       '--checkpoint',exp04/'checkpoints/baseline_final/best.pt','--manifest',exp04/'data'/filename,
       '--data-root',exp04/'data','--dataset',ds,'--output',runtime/'clean'/f'{ds}.json'],runtime/f'clean-{ds}.log')
  run('validation_smoke',[CODE/'smoke.py','--exp04',exp04,'--runtime',runtime,'--profile',a.profile],runtime/'smoke.log')
  assert read(runtime/'smoke.json')['passed']
  for ds in DATASETS:
   run('full_'+ds,[CODE/'run_exp05.py','--exp04',exp04,'--runtime',runtime,'--profile',a.profile,'--dataset',ds],runtime/f'full-{ds}.log')
   run('audit_'+ds,[CODE/'analyze_exp05.py','--runtime',runtime,'--dataset',ds],runtime/f'audit-{ds}.log')
   state['datasets'][ds]['complete']=True;write(status,state)
  state['stage']='complete';state['complete']=True;state['finished_utc']=datetime.now(timezone.utc).isoformat();write(status,state)
  print('EXP05_QUEUE_COMPLETE',flush=True)
 except BaseException as error:
  state['failed_stage']=state['stage'];state['stage']='failed';state['error']=str(error);write(status,state)
  raise


if __name__=='__main__':main()
