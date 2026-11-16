"""Frozen WGN, shared EXP-004 adapters and immutable EXP-005 identities."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys

import torch

CODE=Path(__file__).resolve().parent
REPO=CODE.parents[2]
SHARED=REPO/'experiments/EXP-004-ADVERSARIAL-WGN/code'
sys.path.insert(0,str(SHARED))
from evaluation_data import load_records,cohort_fingerprint,load_source,ffpp_pair_mapping,source_cluster
from image_quality import image_quality
from diagnostics import WGSADiagnostics,compare_diagnostics
from run_exp04_v2 import REFERENCE_SHA,evaluation_summary
from jia_faa import frequency_norm
from run_exp04_v3 import save_example

DATASETS={
 'ffpp':('FaceForensics++-official.json','final_ffpp_reconstruction_001','final_ffpp.json','clean_ffpp_c23.json'),
 'celebdf':('Celeb-DF-v2-official-direct.json','final_celebdf_full_reconstruction_001','full_celebdf.json','clean_celebdf.json'),
 'dfdc':('DFDC.json','final_dfdc_full_reconstruction_001','full_dfdc.json','clean_dfdc.json'),
 'wilddeepfake':('WildDeepfake.json','final_wilddeepfake_full_reconstruction_001','full_wilddeepfake.json','clean_wilddeepfake.json'),
}
METHODS=('stat-init-control','mstat-init-control','hou-statattack-wgn-adapted','hou-mstatattack-reconstruction')


def read(path):return json.loads(Path(path).read_text())


def sha(path):
 with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temporary=path.with_suffix(path.suffix+'.tmp')
 temporary.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n');temporary.replace(path)


def record_id(record,data_root):
 return hashlib.sha256(record.path.resolve().relative_to(data_root.resolve()).as_posix().encode()).hexdigest()[:16]


def load_model(checkpoint,device='cuda'):
 if sha(checkpoint)!=REFERENCE_SHA:raise ValueError('Frozen checkpoint checksum mismatch')
 load_source(REPO)
 from wgn.model import WaveletGuidedNetwork
 payload=torch.load(checkpoint,map_location='cpu',weights_only=False)
 config=payload['config'];cfg=config['model']
 model=WaveletGuidedNetwork(pretrained=False,backbone_name=cfg['backbone'],gate_hidden_dim=cfg['gate_hidden_dim'])
 model.load_state_dict(payload['model'],strict=True)
 return model.to(device).eval().requires_grad_(False),config


def pooled_features(model,images):
 fused,_=model.forward_features(images)
 return fused.mean((2,3))


def model_hash(model):
 h=hashlib.sha256()
 for name,value in model.state_dict().items():
  h.update(name.encode());h.update(value.detach().cpu().contiguous().numpy().tobytes())
 return h.hexdigest()


def source_hashes():
 victim_source=REPO/'experiments/EXP-002-WGN/reproduction/code/src/wgn'
 return {str(p.relative_to(REPO)):sha(p) for root in (CODE,SHARED,victim_source) for p in sorted(root.glob('*.py'))}
