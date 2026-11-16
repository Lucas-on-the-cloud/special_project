"""Postprocess EXP-004 per-frame logs: per-manip ASR, video AUC, video bootstrap CI.

The unit of resampling for uncertainty is a source video, not a frame.
No target data is used for attack selection.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
from paper_aligned_attacks import METHODS
from sklearn.metrics import roc_auc_score

def aggregate(rows):
    videos=defaultdict(list)
    for row in rows:
        videos[(row["manipulation"],row["video"],row["label"])].append(row)
    video_records=[]
    for (manip,video,label),recs in sorted(videos.items()):
        video_records.append({"manipulation":manip,"video":video,"label":label,
            "clean_score":sum(x["clean_score"] for x in recs)/len(recs),
            "attacked_score":sum(x["attacked_score"] for x in recs)/len(recs),
            "frames":len(recs)})
    return video_records

def fake_asr(rows):
    eligible=[r for r in rows if r["label"]==1 and r["clean_score"]>=.5]
    return (sum(r["attacked_score"]<.5 for r in eligible)/len(eligible)) if eligible else None

def counts(rows):
    eligible=[r for r in rows if r['label']==1 and r['clean_score']>=.5]
    return {'eligible_clean_correct_fake':len(eligible),
            'fake_to_real_flips':sum(r['attacked_score']<.5 for r in eligible),
            'asr_conditional':fake_asr(rows)}

def mechanism_groups(rows):
    """Descriptive association, not a causal WGSA attribution."""
    eligible=[r for r in rows if r['label']==1 and r['clean_score']>=.5]
    result={}
    for name,selected in [('success',[r for r in eligible if r['attacked_score']<.5]),
                          ('failure',[r for r in eligible if r['attacked_score']>=.5])]:
        fields=['mean_mae','abs_mean_mae','variance_mae','energy_mae','gates_mae','attention_mae',
                'linf','dct_linf','dct_l2','mse','psnr_db','ssim']
        result[name]={'frames':len(selected)}
        for field in fields:
            values=[r[field] for r in selected if r.get(field) is not None]
            result[name][field+'_mean']=sum(values)/len(values) if values else None
    return result

def video_auc(rows,field):
    y=[r["label"] for r in rows]
    return float(roc_auc_score(y,[r[field] for r in rows])) if len(set(y))==2 else None

def cluster_bootstrap_asr(rows,repeats=1000,seed=1024):
    # Resample source videos; all manipulation variants with the same video ID
    # are kept together within a bootstrap replicate.
    groups=defaultdict(list)
    for r in rows:
        groups[r.get('source_cluster',r['video'])].append(r)
    keys=sorted(groups)
    if len(keys)<2:return None
    rng=random.Random(seed);values=[]
    for _ in range(repeats):
        sample=[r for _ in keys for r in groups[rng.choice(keys)]]
        result=fake_asr(sample)
        if result is not None:values.append(result)
    if not values:return None
    values.sort()
    return [values[int(.025*(len(values)-1))],values[int(.975*(len(values)-1))]]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--run",type=Path,required=True)
    p.add_argument("--method",required=True,choices=(*METHODS,'clean','frequency-init-control','jia-faa-reconstruction'))
    p.add_argument("--bootstrap",type=int,default=1000)
    a=p.parse_args()
    frames=[json.loads(line) for line in (a.run/(a.method+"_per_frame.jsonl")).read_text().splitlines() if line.strip()]
    videos=aggregate(frames)
    manip={}
    for group in sorted(set(r["manipulation"] for r in frames if r["label"]==1)):
        selected=[r for r in frames if r["manipulation"]==group]
        manip[group]={"total_fake_frames":len(selected),**counts(selected),'mechanism':mechanism_groups(selected)}
    output={"attack":a.method,"frame_asr":fake_asr(frames),
        "frame_asr_95pct_cluster_bootstrap":cluster_bootstrap_asr(frames,a.bootstrap),
        "video_count":len(videos),"clean_video_auc":video_auc(videos,"clean_score"),
        "attacked_fake_clean_real_video_auc":video_auc(videos,"attacked_score"),
        "video_fake_asr":fake_asr(videos),"by_manipulation":manip,
        'frame_counts':counts(frames),'video_counts':counts(videos),
        'mechanism_success_vs_failure':mechanism_groups(frames),
        'bootstrap_clusters':len({r.get('source_cluster',r['video']) for r in frames}),
        'interpretation':'diagnostic associations only; external dataset video/sequence IDs may lack shared original-source linkage; intervals exploratory'}
    path=a.run/(a.method+"_video_analysis.json")
    path.write_text(json.dumps(output,indent=2))
    print(json.dumps(output,indent=2))
if __name__=="__main__":main()
