"""Validation-only WGN integration/VRAM benchmark before automatic full runs."""
import argparse
from collections import defaultdict
from pathlib import Path
import random
import time

import torch
from torch.utils.data import DataLoader,Subset

from common import *
from statistical_attack import AttackConfig,attack,reference_indices
from run_exp05 import bank_features,padded_scores


def main():
 p=argparse.ArgumentParser()
 for key in ('exp04','runtime','profile'):p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();exp04=a.exp04.resolve();runtime=a.runtime.resolve()
 torch.set_num_threads(4);torch.manual_seed(1024);torch.backends.cudnn.benchmark=False
 profile=read(a.profile);config=AttackConfig(**profile['attack']);config.validate()
 model,model_config=load_model(exp04/'checkpoints/baseline_final/best.pt')
 initial=model_hash(model)
 from wgn.data import FaceForensicsJsonDataset
 records=load_records(REPO,exp04/'data/FaceForensics++-official.json',exp04/'data',model_config,'ffpp',split='val')
 buckets=defaultdict(list)
 for i,r in enumerate(records):
  if r.label==1:buckets[(r.manipulation,r.video)].append(i)
 rng=random.Random(1024);keys=sorted(buckets);rng.shuffle(keys)
 for values in buckets.values():rng.shuffle(values)
 chosen=sorted(buckets[key][0] for key in keys[:120])
 assert len(chosen)==120 and all(records[i].label==1 for i in chosen)
 references=bank_features(model,runtime,read(runtime/'reference-bank.json'))
 outputs={}
 for method in METHODS:
  torch.cuda.reset_peak_memory_stats();start=time.monotonic();done=0;traces=[]
  for batch in DataLoader(Subset(FaceForensicsJsonDataset(records,train=False),chosen),batch_size=30,num_workers=4):
   x=batch['image'].cuda()
   with torch.no_grad():
    assert torch.allclose(model.classifier(pooled_features(model,x)).squeeze(1),model(x),atol=1e-6,rtol=1e-5)
   ids=reference_indices(done,len(x),len(references))
   out,trace=attack(lambda z:pooled_features(model,z),x,references[ids].detach(),config,
                    multilayer='mstat' in method,initialize_only=method.endswith('init-control'))
   expected_updates=0 if method.endswith('init-control') else 40
   assert trace['updates']==expected_updates and trace['trace'][-1]['update']==expected_updates
   assert out.min()>=0 and out.max()<=1 and (out-x).abs().max()<=config.total_epsilon+1e-6
   with torch.no_grad():
    scores,_=padded_scores(model,out)
    quality=image_quality(x,out)
   if done==0:
    target=runtime/'smoke-examples'/method
    if not target.exists():save_example(target,x[0],out[0])
   done+=len(x);traces.append(trace)
   print(json.dumps({'event':'smoke_progress','method':method,'frames':done,'total':120}),flush=True)
  torch.cuda.synchronize()
  assert model_hash(model)==initial and done==120
  outputs[method]={'frames':done,'seconds':time.monotonic()-start,
      'peak_allocated_mib':torch.cuda.max_memory_allocated()/2**20,'batches':traces}
 write(runtime/'smoke.json',{'passed':True,'split':'FF++ validation only','frames':120,'methods':outputs,
      'profile_sha256':sha(a.profile),'checkpoint_sha256':REFERENCE_SHA,'reference_bank_sha256':sha(runtime/'reference-bank.json'),
      'model_unchanged':True,'feature_adapter_matches_classifier':True,
      'interpretation':'software/VRAM benchmark; not final-test attack selection or publishable ASR'})
 print('EXP05_SMOKE_PASSED',flush=True)


if __name__=='__main__':main()
