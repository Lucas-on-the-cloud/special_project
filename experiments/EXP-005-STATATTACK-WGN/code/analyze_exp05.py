"""Coverage/budget/reference audit and compact full-cohort EXP-005 report."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from common import *
from analyze_by_video import aggregate,counts,cluster_bootstrap_asr,video_auc,mechanism_groups
from summarize_final import diagnostics
from statistical_attack import reference_indices


def main():
 p=argparse.ArgumentParser()
 p.add_argument('--runtime',type=Path,required=True);p.add_argument('--dataset',choices=DATASETS,required=True)
 a=p.parse_args();runtime=a.runtime.resolve();folder=runtime/'runs'/('full_'+a.dataset)
 final=read(folder/'results.json');assert final['complete']
 meta=final['metadata'];identity=meta['identity'];lock=read(folder/'cohort-lock.json')
 expected=lock['cohort']['records'];eligible_indices=lock['eligible_indices']
 assert len(expected)==identity['frames'] and len(eligible_indices)==identity['eligible']
 for relative,digest in identity['source_sha256'].items():assert sha(folder/'source'/relative)==digest
 result={'dataset':a.dataset,'metadata':meta,'methods':{},'complete':True,
   'scope':'full processed test; canonical Fake-to-Real eligibility; frozen WGN; train-Real-guided adaptation',
   'fidelity':'StatAttack source-adapted40; MStatAttack reconstruction; not original Hou table reproduction',
   'evidence_sha256':{'results.json':sha(folder/'results.json')},'paired_controls':{}}
 all_rows={};first_clean=None
 for method in METHODS:
  path=folder/(method+'_per_frame.jsonl')
  rows=[json.loads(line) for line in path.read_text().splitlines()]
  assert len(rows)==len(expected) and len({r['record_id_sha256_16'] for r in rows})==len(rows)
  clean_identity=[(r['record_id_sha256_16'],r['clean_score']) for r in rows]
  if first_clean is None:first_clean=clean_identity
  else:assert clean_identity==first_clean
  for i,(original,r) in enumerate(zip(expected,rows)):
   assert r['record_id_sha256_16']==hashlib.sha256(original['path'].encode()).hexdigest()[:16]
   assert (r['label'],r['video'],r['manipulation'])==(original['label'],original['video'],original['manipulation'])
   eligible=r['label']==1 and r['clean_score']>=.5
   assert r['attack_applied']==eligible
   assert 0<=r['attacked_score']<=1 and r['linf']<=identity['profile']['attack']['total_epsilon']+1e-6
   if not eligible:assert r['attacked_score']==r['clean_score'] and r['linf']==r['dct_linf']==r['dct_l2']==0
  batches_path=folder/(method+'_batches.jsonl')
  traces=[json.loads(line) for line in batches_path.read_text().splitlines()]
  covered=[];offset=0
  for number,t in enumerate(traces):
   assert t['batch']==number and t['offset']==offset and 0<t['frames']<=30
   assert t['updates']==(0 if method.endswith('init-control') else 40)
   assert t['reference_indices']==reference_indices(offset,t['frames'],960)
   covered+=t['record_ids'];offset+=t['frames']
  assert covered==[rows[i]['record_id_sha256_16'] for i in eligible_indices] and offset==len(eligible_indices)
  videos=aggregate(rows);c=counts(rows);summary=final['results'][method]
  assert c['fake_to_real_flips']==summary['fake_to_real_flips'] and c['eligible_clean_correct_fake']==identity['eligible']
  eligible=[r for r in rows if r['attack_applied']]
  analysis={'frame_counts':c,'frame_asr_95pct_cluster_bootstrap':cluster_bootstrap_asr(rows,1000),
     'video_counts':counts(videos),'video_count':len(videos),'clean_video_auc':video_auc(videos,'clean_score'),
     'attacked_fake_clean_real_video_auc':video_auc(videos,'attacked_score'),
     'mechanism_success_vs_failure':mechanism_groups(rows),
     'eligible_quality_and_diagnostics':diagnostics(eligible),
     'mmd_clean_mean':float(np.mean([t['clean_mmd'] for t in traces])),
     'mmd_initial_mean':float(np.mean([t['trace'][0]['mmd'] for t in traces])),
     'mmd_final_mean':float(np.mean([t['trace'][-1]['mmd'] for t in traces]))}
  result['methods'][method]={'summary':summary,'analysis':analysis}
  result['evidence_sha256'][path.name]=sha(path);result['evidence_sha256'][batches_path.name]=sha(batches_path)
  all_rows[method]=rows
 for method,control in [('hou-statattack-wgn-adapted','stat-init-control'),('hou-mstatattack-reconstruction','mstat-init-control')]:
  arows=all_rows[method];brows=all_rows[control]
  aa=np.array([arows[i]['attacked_score']<.5 for i in eligible_indices],dtype=int)
  bb=np.array([brows[i]['attacked_score']<.5 for i in eligible_indices],dtype=int)
  result['paired_controls'][method]={'eligible':len(aa),'both':int(((aa==1)&(bb==1)).sum()),
    'method_only':int(((aa==1)&(bb==0)).sum()),'control_only':int(((aa==0)&(bb==1)).sum()),
    'neither':int(((aa==0)&(bb==0)).sum()),'asr_difference':float((aa-bb).mean())}
 result['audits_passed']=['full cohort/labels/unique IDs','canonical clean pairing and eligibility','unchanged Real/FN',
    'total RGB bounds','complete fixed-step batch coverage','equal-size cyclic train-Real references','source snapshots',
    'summary/per-frame count agreement']
 output=CODE.parent/'results';output.mkdir(exist_ok=True)
 write(output/(a.dataset+'-evaluation.json'),result)
 lines=[f'# EXP-005 — Full {a.dataset}','',result['scope'],
   '',result['fidelity'],'',f"Frames: {identity['frames']:,}; eligible Fake: {identity['eligible']:,}.",'',
   '| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |','|---|---:|---:|---:|']
 for method,value in result['methods'].items():
  s=value['summary'];lines.append(f"| {method} | {s['fake_to_real_flips']:,}/{s['eligible_clean_correct_fake']:,} | {100*s['asr_fake_given_clean_correct']:.2f}% | {s['attacked_fake_clean_real_frame_auc']:.6f} |")
 lines+=['','Total pixel L∞≤60/255; each layer noise≤4/255; those are distinct. Optimized methods use40 updates; MStat has3 layers. MMD, reference access and budgets differ from Jia; ASR alone does not rank equal strength. Real and baseline false-negative Fake are unchanged. Diagnostics are associations, without causal WGSA attribution. External sequence/video intervals remain exploratory without original-source linkage. BRISQUE was not evaluated; PSNR/SSIM and finite counts are in JSON.',
   '',f'[Compact evidence]({a.dataset}-evaluation.json). [Algorithm specification](../docs/HOU-ALGORITHM-SPEC.md). All recorded coverage/reference/budget audits passed.','']
 (output/(a.dataset+'-report.md')).write_text('\n'.join(lines))
 print('EXP05_AUDIT_PASSED '+a.dataset,flush=True)


if __name__=='__main__':main()
