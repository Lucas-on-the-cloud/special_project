"""Resumable full frozen-WGN statistical attacks; no training or test tuning."""
from __future__ import annotations

import argparse
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import random
import shutil
import sqlite3
import time

import numpy as np
import torch
from torch.utils.data import DataLoader,Subset

from common import *
from statistical_attack import AttackConfig,attack,reference_indices,finite

PRE_BATCH_PARITY_RUNNER_SHA256='aaab0bd1f27ccbc036ed8ae56a35ad03f0d2b1ed9a8e792e48ca289c3d4e5384'
RUNNER_RELATIVE='experiments/EXP-005-STATATTACK-WGN/code/run_exp05.py'


def migrate_interrupted_dfdc(metadata_path,folder,identity):
 """Narrow, auditable migration for the known clean-score batch-shape interruption."""
 old=read(metadata_path);old_identity=old['identity']
 if old_identity==identity:return
 if identity['dataset']!='dfdc' or old_identity.get('dataset')!='dfdc':
  raise ValueError('Only the specifically audited interrupted DFDC run can be migrated')
 old_sources=old_identity['source_sha256'];new_sources=identity['source_sha256']
 if set(old_sources)!=set(new_sources):raise ValueError('Resume source set changed')
 changed=[name for name in old_sources if old_sources[name]!=new_sources[name]]
 if changed!=[RUNNER_RELATIVE] or old_sources[RUNNER_RELATIVE]!=PRE_BATCH_PARITY_RUNNER_SHA256:
  raise ValueError('Resume has source changes beyond the reviewed clean-score parity fix')
 comparable_old=dict(old_identity);comparable_new=dict(identity)
 comparable_old.pop('source_sha256');comparable_new.pop('source_sha256')
 if comparable_old!=comparable_new:raise ValueError('DFDC cohort/profile/model/reference identity changed')
 snapshot=folder/'source'/RUNNER_RELATIVE
 if sha(snapshot)!=PRE_BATCH_PARITY_RUNNER_SHA256:raise ValueError('Prior runner snapshot does not match the interrupted run')
 db=sqlite3.connect(folder/'state.sqlite')
 try:
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('DFDC resume database is corrupt')
  frame_counts=dict(db.execute('SELECT method,COUNT(*) FROM frames GROUP BY method').fetchall())
  batch_counts={m:(n,frames) for m,n,frames in db.execute(
      "SELECT method,COUNT(*),SUM(json_extract(data,'$.frames')) FROM batches GROUP BY method").fetchall()}
 finally:db.close()
 if frame_counts!={'stat-init-control':42900} or batch_counts!={'stat-init-control':(1430,42900)}:
  raise ValueError('DFDC resume database no longer matches the audited interruption point')
 backup=snapshot.with_name(snapshot.name+'.pre-clean-score-parity')
 if backup.exists():
  if sha(backup)!=PRE_BATCH_PARITY_RUNNER_SHA256:raise ValueError('Existing pre-migration snapshot has unexpected content')
 else:shutil.copyfile(snapshot,backup)
 shutil.copyfile(REPO/RUNNER_RELATIVE,snapshot)
 if sha(snapshot)!=new_sources[RUNNER_RELATIVE]:raise ValueError('Updated DFDC runner snapshot failed hash verification')
 old['identity']=identity
 old.setdefault('resume_migrations',[]).append({
  'at_utc':datetime.now(timezone.utc).isoformat(),
  'reason':'The prior exact FP32 clean-score comparison rejected harmless CUDA batch-shape numerical drift.',
  'clean_verification':'Canonical EXP-004 eligibility and threshold are immutable; fresh batch score must preserve the clean class at threshold 0.5; record rechecked score and absolute delta.',
  'attack_profile_or_cohort_changed':False,
  'runner_before_sha256':PRE_BATCH_PARITY_RUNNER_SHA256,
  'runner_after_sha256':new_sources[RUNNER_RELATIVE],
  'sqlite_integrity':'ok','committed_frames_before_resume':frame_counts,
  'committed_batches_before_resume':{m:{'batches':v[0],'frames':v[1]} for m,v in batch_counts.items()},
  'preserved_previous_runner_snapshot':backup.name})
 write(metadata_path,old)


def bank_features(model,runtime,bank,batch_size=32):
 from wgn.data import FrameRecord,FaceForensicsJsonDataset
 cache=runtime/'reference-features.pt'
 identity={'bank_sha256':sha(runtime/'reference-bank.json'),'model_sha256':model_hash(model),
           'layer':'fused spatial mean before classifier','batch_size':batch_size}
 for r in bank['records']:
  if sha(runtime/'reference-data'/r['path'])!=r['image_sha256']:raise ValueError('Reference image changed')
 if cache.exists():
  saved=torch.load(cache,map_location='cpu',weights_only=False)
  if saved['identity']!=identity:raise ValueError('Reference feature cache identity changed')
  return saved['features'].cuda()
 records=[FrameRecord(runtime/'reference-data'/r['path'],0,r['video'],'FF-real') for r in bank['records']]
 features=[]
 with torch.no_grad():
  for batch in DataLoader(FaceForensicsJsonDataset(records,train=False),batch_size=batch_size,num_workers=4):
   features.append(pooled_features(model,batch['image'].cuda()).cpu())
 result=torch.cat(features)
 finite(result,'reference cache')
 temporary=cache.with_suffix('.partial');torch.save({'identity':identity,'features':result},temporary);temporary.replace(cache)
 return result.cuda()


def padded_scores(model,x,hook=None):
 n=len(x)
 if not 0<n<=32:raise ValueError('Scoring requires at most32 images')
 padded=torch.cat((x,x[:1].expand(32-n,-1,-1,-1))) if n<32 else x
 scores=model(padded).sigmoid()[:n]
 finite(scores,'scores')
 diag={k:v[:n].clone() for k,v in hook.current.items()} if hook else None
 return scores,diag


def unchanged(original):
 row=dict(original)
 row.update(attacked_score=row['clean_score'],attack_applied=False,linf=0.,dct_linf=0.,dct_l2=0.,
            mse=0.,psnr_db=None,ssim=1.)
 for name in ('mean','abs_mean','variance','energy','gates','attention'):
  row[name+'_mae']=0.
  if name!='attention':row[name+'_attacked']=list(row[name+'_clean'])
 return row


def connect(path):
 db=sqlite3.connect(path)
 db.execute('PRAGMA journal_mode=WAL')
 db.execute('CREATE TABLE IF NOT EXISTS frames(method TEXT, idx INTEGER, data TEXT, PRIMARY KEY(method,idx))')
 db.execute('CREATE TABLE IF NOT EXISTS batches(method TEXT, batch INTEGER, data TEXT, PRIMARY KEY(method,batch))')
 db.commit();return db


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('exp04','runtime','profile'):p.add_argument('--'+key,type=Path,required=True)
 p.add_argument('--dataset',choices=DATASETS,required=True)
 a=p.parse_args();exp04=a.exp04.resolve();runtime=a.runtime.resolve()
 profile=read(a.profile);config=AttackConfig(**profile['attack']);config.validate()
 if profile['methods']!=list(METHODS) or profile['datasets']!=list(DATASETS) or profile['reference_bank_size']!=960:
  raise ValueError('Unexpected locked methods/datasets/reference bank')
 if profile['optimization_batch']!=30 or profile['evaluation_batch']!=32:raise ValueError('Unexpected locked grouping')
 if not torch.cuda.is_available():raise RuntimeError('CUDA required')
 torch.set_num_threads(4);torch.backends.cudnn.benchmark=False
 random.seed(profile['seed']);np.random.seed(profile['seed']);torch.manual_seed(profile['seed'])
 checkpoint=exp04/'checkpoints/baseline_final/best.pt'
 model,model_config=load_model(checkpoint)
 initial_model_hash=model_hash(model)
 from wgn.data import FaceForensicsJsonDataset
 filename,prior_run,cohort_file,prior_clean=DATASETS[a.dataset]
 manifest=exp04/'data'/filename;data_root=exp04/'data'
 records=load_records(REPO,manifest,data_root,model_config,a.dataset)
 cohort=read(exp04/'cohorts'/cohort_file)
 gate=read(runtime/'clean'/f'{a.dataset}.json')
 fingerprint=cohort_fingerprint(records,data_root)
 assert fingerprint==cohort['cohort_fingerprint']==gate['portable_cohort_fingerprint'] and gate['passed']
 assert sha(manifest)==gate['manifest_sha256'] and sha(checkpoint)==gate['checkpoint_sha256']
 previous=exp04/'runs'/prior_run
 assert read(previous/'results.json')['complete'] is True
 canonical=[json.loads(line) for line in (previous/'fgsm_per_frame.jsonl').read_text().splitlines()]
 assert len(canonical)==len(records) and len({r['record_id_sha256_16'] for r in canonical})==len(records)
 for record,row in zip(records,canonical):
  assert record_id(record,data_root)==row['record_id_sha256_16']
  assert (record.label,record.video,record.manipulation)==(row['label'],row['video'],row['manipulation'])
 eligible=[i for i,row in enumerate(canonical) if row['label']==1 and row['clean_score']>=.5]
 bank=read(runtime/'reference-bank.json');assert bank['complete'] and len(bank['records'])==960
 references=bank_features(model,runtime,bank)
 folder=runtime/'runs'/('full_'+a.dataset);folder.mkdir(parents=True,exist_ok=True)
 identity={'dataset':a.dataset,'cohort_fingerprint':fingerprint,'frames':len(records),'eligible':len(eligible),
   'model_tensor_sha256':initial_model_hash,
   'profile':profile,'profile_sha256':sha(a.profile),'checkpoint_sha256':sha(checkpoint),'manifest_sha256':sha(manifest),
   'reference_bank_sha256':sha(runtime/'reference-bank.json'),'reference_features_sha256':sha(runtime/'reference-features.pt'),
   'clean_gate_sha256':sha(runtime/'clean'/f'{a.dataset}.json'),
   'canonical_jsonl_sha256':sha(previous/'fgsm_per_frame.jsonl'),'source_sha256':source_hashes()}
 metadata_path=folder/'environment.json'
 if metadata_path.exists():
  migrate_interrupted_dfdc(metadata_path,folder,identity)
  metadata=read(metadata_path);assert metadata['identity']==identity,'Resume identity changed'
 else:
  metadata={'identity':identity,'started_utc':datetime.now(timezone.utc).isoformat(),
   'gpu':torch.cuda.get_device_name(0),'torch':torch.__version__,
   'packages':{k:importlib.metadata.version(k) for k in ('torch','torchvision','timm','numpy','scikit-learn','Pillow')},
   'fidelity':'source-adapted StatAttack40; explicit MStatAttack reconstruction; see HOU-ALGORITHM-SPEC',
   'reference_policy':'FF++ train Real only;960 deterministic frames; cyclic equal-size references',
   'quality_population':'canonical clean-correct Fake; Real/FN unchanged; PSNR null=infinity'}
  write(metadata_path,metadata)
  for relative,digest in identity['source_sha256'].items():
   target=folder/'source'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(REPO/relative,target)
   assert sha(target)==digest
  write(folder/'cohort-lock.json',{'cohort':cohort,'eligible_indices':eligible,'reference_bank_sha256':identity['reference_bank_sha256']})
 db=connect(folder/'state.sqlite')
 hook=WGSADiagnostics(model);summaries={}
 try:
  for method in METHODS:
   torch.manual_seed(profile['seed']);started=time.monotonic();torch.cuda.reset_peak_memory_stats()
   multi='mstat' in method;control=method.endswith('init-control')
   traces=[json.loads(r[0]) for r in db.execute('SELECT data FROM batches WHERE method=? ORDER BY batch',(method,))]
   completed=sum(t['frames'] for t in traces)
   assert completed==db.execute('SELECT COUNT(*) FROM frames WHERE method=?',(method,)).fetchone()[0]
   if completed==len(eligible) and (folder/(method+'_summary.json')).exists() and (folder/(method+'_per_frame.jsonl')).exists():
    summaries[method]=read(folder/(method+'_summary.json'));continue
   remaining=eligible[completed:]
   loader=DataLoader(Subset(FaceForensicsJsonDataset(records,train=False),remaining),
       batch_size=profile['optimization_batch'],num_workers=4,shuffle=False,pin_memory=True)
   for batch in loader:
    batch_started=time.monotonic()
    n=len(batch['image']);indices=eligible[completed:completed+n]
    ids=[canonical[i]['record_id_sha256_16'] for i in indices]
    for i,path in zip(indices,batch['path']):assert Path(path)==records[i].path
    x=batch['image'].cuda(non_blocking=True)
    with torch.no_grad():before_score,before=padded_scores(model,x,hook)
    expected=torch.tensor([canonical[i]['clean_score'] for i in indices],device=x.device)
    if not torch.equal(before_score>=.5,expected>=.5):
     raise ValueError('Canonical clean class changed under declared scoring batch')
    clean_score_delta=(before_score-expected).abs()
    ref_ids=reference_indices(completed,n,len(references))
    hook.enabled=False
    try:adv,details=attack(lambda z:pooled_features(model,z),x,references[ref_ids].detach(),config,
                           multilayer=multi,initialize_only=control)
    finally:hook.enabled=True
    with torch.no_grad():
     scores,after=padded_scores(model,adv,hook)
     quality=image_quality(x,adv);delta=adv-x
     linf=delta.abs().flatten(1).amax(1)
     dct_linf=frequency_norm(delta,8,'linf');dct_l2=frequency_norm(delta,8,'l2')
    rows=[]
    for j,i in enumerate(indices):
     drift=compare_diagnostics({k:v[j:j+1] for k,v in before.items()},{k:v[j:j+1] for k,v in after.items()})
     row={**canonical[i],**drift,**quality[j], 'clean_score':canonical[i]['clean_score'],
          'clean_score_rechecked':float(before_score[j]),
          'clean_score_recheck_abs_delta':float(clean_score_delta[j]),
          'attacked_score':float(scores[j]),'attack_applied':True,
          'linf':float(linf[j]),'dct_linf':float(dct_linf[j]),'dct_l2':float(dct_l2[j]),'batch_index':len(traces)}
     assert row['linf']<=config.total_epsilon+1e-6
     rows.append((method,i,json.dumps(row,allow_nan=False)))
    details.update(batch=len(traces),frames=n,offset=completed,record_ids=ids,reference_indices=ref_ids,
                   seconds=time.monotonic()-batch_started)
    with db:
     db.executemany('INSERT INTO frames VALUES(?,?,?)',rows)
     db.execute('INSERT INTO batches VALUES(?,?,?)',(method,len(traces),json.dumps(details,allow_nan=False)))
    if completed==0 and not (folder/'examples'/method).exists():
     temp=folder/'examples'/(method+'.partial')
     if temp.exists():shutil.rmtree(temp)
     save_example(temp,x[0],adv[0]);temp.rename(folder/'examples'/method)
    completed+=n;traces.append(details)
    progress={'event':'attack_progress','dataset':a.dataset,'method':method,'eligible_completed':completed,
              'eligible_total':len(eligible),'updates':details['updates'],'mmd_final':details['trace'][-1]['mmd']}
    write(folder/'progress.json',progress);print(json.dumps(progress),flush=True)
   assert completed==len(eligible)
   modified={index:json.loads(row) for index,row in db.execute('SELECT idx,data FROM frames WHERE method=?',(method,))}
   rows=[modified[i] if i in modified else unchanged(row) for i,row in enumerate(canonical)]
   target=folder/(method+'_per_frame.jsonl');temporary=target.with_suffix('.tmp')
   with temporary.open('w') as stream:
    for row in rows:stream.write(json.dumps(row,allow_nan=False)+'\n')
   temporary.replace(target)
   trace_path=folder/(method+'_batches.jsonl')
   with trace_path.open('w') as stream:
    for t in traces:stream.write(json.dumps(t,allow_nan=False)+'\n')
   summary=evaluation_summary(rows,method)
   summary.update(seconds_this_process=time.monotonic()-started,peak_allocated_mib=torch.cuda.max_memory_allocated()/2**20,
                  completed_batches=len(traces),optimization_updates=0 if control else config.steps,
                  optimization_batches_seconds=sum(t['seconds'] for t in traces))
   assert model_hash(model)==initial_model_hash
   write(folder/(method+'_summary.json'),summary);summaries[method]=summary
   print('METHOD_COMPLETE '+json.dumps(summary),flush=True)
  write(folder/'results.json',{'metadata':metadata,'results':summaries,'complete':True,
                             'finished_utc':datetime.now(timezone.utc).isoformat()})
  print('EXP05_DATASET_COMPLETE '+a.dataset,flush=True)
 finally:hook.close();db.close()


if __name__=='__main__':main()
