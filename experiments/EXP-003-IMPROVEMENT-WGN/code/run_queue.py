"""Single-GPU queue: preflight -> controls/pilots/finals -> locked evaluation -> GitHub."""
from __future__ import annotations

import argparse
import atexit
import ctypes
from datetime import datetime, timedelta, timezone
import json
import math
import msvcrt
import os
from pathlib import Path
import subprocess
import sys
import time

import common
from common import ROOT, atomic_json, config_load

RUNS=Path('C:/sp/runs/wgn_overnight')
REPO=ROOT.parents[2]
REFERENCE_CONFIG=REPO/'experiments'/'EXP-002-WGN'/'reproduction'/'code'/'configs'/'wgn_ffpp_c23_rtx5060.yaml'
METHODS=['baseline','gradient','curriculum','temporal_control','temporal',
         'degradation_control','degradation_consistency']
TZ=timezone(timedelta(hours=7))


def config_for(method):
    return REFERENCE_CONFIG if method == 'baseline' else ROOT/'configs'/f'{method}.yaml'


def now():
    return datetime.now(TZ).isoformat(timespec='seconds')


class Queue:
    def __init__(self):
        RUNS.mkdir(parents=True,exist_ok=True)
        (RUNS/'logs').mkdir(exist_ok=True)
        self.lock=(RUNS/'queue.lock').open('a+b')
        self.lock.seek(0)
        if not self.lock.read(1):
            self.lock.write(b'0')
            self.lock.flush()
        self.lock.seek(0)
        msvcrt.locking(self.lock.fileno(),msvcrt.LK_NBLCK,1)
        self.stages={}
        state=RUNS/'queue-status.json'
        if state.exists():
            self.stages=json.loads(state.read_text()).get('stages',{})
        # Prevent idle system sleep only while the queue process is alive.
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
        atexit.register(lambda:ctypes.windll.kernel32.SetThreadExecutionState(0x80000000))
        (RUNS/'queue.pid').write_text(str(os.getpid()),encoding='ascii')
        self.phase='starting'
        self.write_status()

    def write_status(self):
        from report import generate
        generate()
        state={'updated_at':now(),'pid':os.getpid(),'phase':self.phase,'stages':self.stages,
               'datasets':{name:Path(f'C:/sp/data/{name}.json').exists()
                           for name in ['FaceForensics++-official','Celeb-DF-v2-official-direct',
                                        'DFDC','WildDeepfake']}}
        rows=[]
        for method in METHODS:
            run=RUNS/f'{method}_final'
            progress=run/'progress.json'
            values=json.loads(progress.read_text()) if progress.exists() else {}
            best=values.get('best_val',{})
            if 'last' in values:
                best=values['last']['val']
            rows.append(f"| {method} | {values.get('status','queued')} | {values.get('completed_epochs',0)}/25 | "
                        f"{best.get('accuracy','-')} | {best.get('auc','-')} | "
                        f"{'uploaded' if (run/'github-upload.json').exists() else 'pending'} |")
        atomic_json(RUNS/'queue-status.json',state)
        (RUNS/'STATUS.md').write_text(
            '# WGN overnight queue\n\n'+f'Updated: {state["updated_at"]}\n\nPhase: **{self.phase}**\n\n'
            +'| Model | Status | Epochs | Latest validation accuracy | Latest validation AUC | GitHub |\n'
            +'|---|---|---|---|---|---|\n'+'\n'.join(rows)+'\n\n'
            +'Synthetic smoke tests validate code only; they are not detection results.\n\n'
            +'See queue-status.json for stage failures; logs/ for full output.\n\n'
            +'External evaluation waits for the complete approved test manifests. Missing targets are explicitly pending.\n\n'
            +'This queue continues until all configured jobs finish. STOP_AFTER_CURRENT requests a graceful stop.\n',
            encoding='utf-8')

    def event(self,message):
        print(f'{now()} {message}',flush=True)
        with (RUNS/'events.jsonl').open('a',encoding='utf-8') as handle:
            handle.write(json.dumps({'time':now(),'message':message})+'\n')

    def run(self,name,arguments,retries=0,skip_completed=True):
        if skip_completed and self.stages.get(name,{}).get('status')=='complete':
            return True
        if (RUNS/'STOP_AFTER_CURRENT').exists():
            self.phase='stopped_by_request'
            self.write_status()
            raise SystemExit(0)
        log=RUNS/'logs'/f'{name}.log'
        for attempt in range(retries+1):
            self.phase=name
            self.stages[name]={'status':'running','started_at':now(),'log':str(log),'attempt':attempt+1}
            self.event(f'START {name}')
            environment=os.environ.copy()
            environment.update(TORCH_HOME='C:/sp/.cache/torch',HF_HOME='C:/sp/.cache/huggingface',
                               PYTHONUNBUFFERED='1',GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
            with log.open('a',encoding='utf-8') as handle:
                handle.write('\nCOMMAND '+json.dumps([str(x) for x in arguments])+'\n')
                handle.flush()
                process=subprocess.Popen([str(x) for x in arguments],stdout=handle,stderr=subprocess.STDOUT,
                                         cwd=ROOT,env=environment)
                self.stages[name]['child_pid']=process.pid
                while process.poll() is None:
                    self.write_status()
                    time.sleep(10)
            code=process.returncode
            self.stages[name].update(status='complete' if code==0 else 'failed',ended_at=now(),returncode=code)
            self.write_status()
            self.event(f'{"COMPLETE" if code==0 else "FAILED"} {name} exit={code}')
            if code==0:
                return True
        return False

    def require(self,*args,**kwargs):
        if not self.run(*args,**kwargs):
            self.phase='failed_required_preflight'
            self.write_status()
            raise SystemExit(1)

    def publish(self,method):
        return self.run(f'publish_{method}',[sys.executable,ROOT/'publish.py','--run',RUNS/f'{method}_final'],
                        retries=2,skip_completed=False)

    def training(self,method,pilot=False):
        name=f'{method}_{"pilot" if pilot else "final"}'
        config=config_for(method)
        arguments=[sys.executable,ROOT/'train.py','--config',config,'--output-dir',RUNS/name,'--resume']
        if pilot:
            arguments+=['--epochs','5','--pilot']
        already_complete=self.stages.get(name,{}).get('status')=='complete'
        success=self.run(name,arguments,retries=1)
        if success and already_complete:
            if pilot:
                return True
            run=RUNS/name
            if (run/'github-upload.json').exists() and (run/'evaluation.json').exists():
                return True
        if success and pilot:
            history=[json.loads(line) for line in (RUNS/name/'metrics.jsonl').read_text().splitlines()]
            if len(history)!=5 or not all(math.isfinite(row['val']['auc']) for row in history):
                self.stages[name]['status']='failed_validation'
                self.write_status()
                return False
            # Report noisy loss trends; do not select methods using a test target.
            self.event(f'PILOT_LOSS {method}: first={history[0]["train"]["loss"]:.6f} '
                       f'last={history[-1]["train"]["loss"]:.6f}')
            if history[-1]['train']['loss'] >= history[0]['train']['loss']:
                self.stages[name]['status']='failed_loss_not_decreasing'
                self.write_status()
                return False
        if success and not pilot:
            self.publish(method)
            if method in METHODS:
                self.run(f'early_evaluate_{method}',[sys.executable,ROOT/'evaluate.py','--run',RUNS/f'{method}_final',
                               '--config',ROOT/'configs'/f'{method}.yaml'],skip_completed=False)
                self.publish(method)
        return success

    def official_celebdf(self):
        archive=Path('C:/sp/data/official-source/Celeb-DF-v2/Celeb-DF-v2-official.zip')
        download_pid=Path('C:/sp/data/official-source/Celeb-DF-v2/download.pid')
        if not archive.exists() and download_pid.exists():
            try:
                pid=int(download_pid.read_text())
            except ValueError:
                pid=0
            if pid:
                self.require('wait_celebdf_official_download',['powershell.exe','-NoProfile','-Command',
                             f'Wait-Process -Id {pid} -ErrorAction SilentlyContinue; exit 0'])
        if not archive.exists():
            self.event('CELEBDF_OFFICIAL_PENDING: author archive is unavailable')
            return False
        smoke_root=RUNS/'smoke'/'celebdf-official'
        smoke_data=Path('C:/sp/data/Celeb-DF-v2-official-smoke')
        smoke_manifest=Path('C:/sp/data/Celeb-DF-v2-official-smoke.json')
        self.require('prepare_celebdf_official_smoke',[sys.executable,ROOT/'prepare_celebdf_official.py',
                     '--smoke','--output',smoke_data,'--manifest',smoke_manifest],retries=1)
        self.require('model_celebdf_official_smoke',[sys.executable,ROOT/'smoke_celebdf_official.py',
                     '--manifest',smoke_manifest,'--config',REFERENCE_CONFIG,
                     '--output',smoke_root/'smoke.json'])
        self.require('prepare_celebdf_official',[sys.executable,ROOT/'prepare_celebdf_official.py'],retries=1)
        for method in METHODS:
            if self.stages.get(f'{method}_final',{}).get('status')=='complete':
                self.run(f'evaluate_celebdf_official_{method}',
                         [sys.executable,ROOT/'evaluate_celebdf_official.py','--run',RUNS/f'{method}_final'],
                         skip_completed=False)
                self.publish(method)
        return True

    def main(self):
        # Smoke tests are repeated by the actual unattended process before any long GPU work.
        for method in METHODS:
            self.require(f'synthetic_smoke_{method}',[sys.executable,ROOT/'smoke_test.py','--synthetic',
                '--config',config_for(method),'--output',RUNS/'smoke'/f'{method}_synthetic.json'])
        report=Path('C:/sp/data/FaceForensics++-official/download-c23-report.json')
        pid_path=Path('C:/sp/runs/setup/ffpp-download.pid')
        if pid_path.exists() and not report.exists():
            pid=int(pid_path.read_text())
            self.require('wait_initial_download',['powershell.exe','-NoProfile','-Command',
                         f'Wait-Process -Id {pid} -ErrorAction SilentlyContinue; exit 0'])
        self.require('prepare_ffpp_c23',[sys.executable,ROOT/'prepare_data.py'],retries=1)
        self.require('validate_ffpp',[sys.executable,ROOT/'preflight.py','--config',REFERENCE_CONFIG,
                                   '--output',RUNS/'preflight.json'])
        self.require('external_smoke',[sys.executable,ROOT/'smoke_external.py','--config',REFERENCE_CONFIG,
                                     '--output',RUNS/'smoke'/'external.json'])
        for method in METHODS:
            self.require(f'real_smoke_{method}',[sys.executable,ROOT/'smoke_test.py','--config',
                          config_for(method),'--output',RUNS/'smoke'/f'{method}_real.json'])
        baseline_ok=self.training('baseline')
        for method in ['gradient','curriculum']:
            if method=='curriculum' and not baseline_ok:
                self.stages['curriculum_final']={'status':'blocked_baseline_failed'}
                continue
            if self.training(method,pilot=True):
                self.training(method)
        # Rebuild the authors' official Celeb-DF test videos with the exact WGN crop pipeline.
        # This is the active Celeb-DF cross-data target for improvement comparisons.
        self.official_celebdf()
        # Run the paired controls after the protocol-sensitivity answer is available.
        self.training('temporal_control')
        if self.training('temporal',pilot=True):
            self.training('temporal')
        if self.training('degradation_control',pilot=True):
            self.training('degradation_control')
        if self.training('degradation_consistency',pilot=True):
            self.training('degradation_consistency')
        # Adds official-direct evaluation for paired checkpoints without reprocessing the videos.
        self.official_celebdf()
        # Preserve training results before slower robustness data preparation.
        c40_ok=self.run('prepare_ffpp_c40',[sys.executable,ROOT/'prepare_data.py','--compression','c40'],retries=1)
        if not c40_ok:
            self.event('C40_PENDING: main/evaluation results will remain available')
        for compression in ['c23','c40']:
            self.run(f'prepare_faceshifter_{compression}',[sys.executable,ROOT/'prepare_data.py',
                         '--compression',compression,'--groups','FF-FSh'],retries=1)
        self.run('import_external',[sys.executable,ROOT/'import_external.py'],skip_completed=False)
        for method in METHODS:
            if self.stages.get(f'{method}_final',{}).get('status')=='complete':
                self.run(f'evaluate_{method}',[sys.executable,ROOT/'evaluate.py','--run',RUNS/f'{method}_final',
                                              '--config',config_for(method)],skip_completed=False)
                self.publish(method)
        self.phase='main_queue_complete'
        self.write_status()
        self.event('MAIN_QUEUE_COMPLETE')
        # The failed curriculum candidate no longer receives eight expensive cross-manipulation runs.
        # Run that matrix later for the selected finalist rather than selecting a method on target tests.
        self.event('CROSS_MANIPULATION_DEFERRED_UNTIL_FINALIST_SELECTED')
        incomplete=[name for name,stage in self.stages.items() if stage.get('status')!='complete']
        self.phase='queue_finished_with_failures' if incomplete else 'queue_complete'
        self.write_status()
        self.event('QUEUE_COMPLETE')


if __name__=='__main__':
    Queue().main()
