"""EXP-004 V2: paper-attributed, fake-to-real adversarial assessment.

Original WGN baseline and manifest are owned by EXP-002. No training.
The main result is conditional fake-to-real ASR on clean-correctly-detected fake
frames, with paired clean-vs-attacked logits and WGSA representations.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import platform
import random
import sys

import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Subset

from paper_aligned_attacks import METHODS, attack
from diagnostics import WGSADiagnostics, compare_diagnostics

REFERENCE_SHA="a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6"

def file_sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def select_pilot(records, maximum, seed):
    """Deterministic round-robin by video, grouped by label+manipulation.
    Ensures both labels, multiple manipulation groups, multiple videos.
    Split selection belongs to the caller; this function only selects indices.
    """
    if maximum<=0 or maximum>=len(records):
        return list(range(len(records)))
    groups=defaultdict(lambda:defaultdict(list))
    for index,record in enumerate(records):
        groups[(int(record.label),record.manipulation)][record.video].append(index)
    if len({k[0] for k in groups})!=2:
        raise ValueError("Cannot create pilot without both binary labels")
    rng=random.Random(seed)
    pool={}
    for group,videos in groups.items():
        order=sorted(videos)
        rng.shuffle(order)
        pool[group]=[]
        remaining=[]
        for video in order:
            indices=sorted(videos[video])
            rng.shuffle(indices)
            pool[group].append(indices[0])
            remaining.extend(indices[1:])
        pool[group]+=remaining
    selection=[]
    by_label={label:sorted(k for k in pool if k[0]==label) for label in (0,1)}
    per_label={0:maximum//2,1:maximum-maximum//2}
    for label in (0,1):
        keys=by_label[label];i=0
        while per_label[label]>0 and any(pool[k] for k in keys):
            k=keys[i%len(keys)]
            if pool[k]:
                selection.append(pool[k].pop(0))
                per_label[label]-=1
            i+=1
    if not selection:raise ValueError("Empty pilot")
    if len(selection)!=len(set(selection)):
        raise AssertionError('Sampler selected duplicate records')
    return sorted(selection)

def parse():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("repo-root","checkpoint","manifest","data-root","output"):
        p.add_argument("--"+name,required=True,type=Path)
    p.add_argument("--compression",default="c23",choices=["c23","c40"])
    p.add_argument("--methods",nargs="+",default=list(METHODS),choices=METHODS)
    p.add_argument("--epsilon",type=float,default=4/255)
    p.add_argument("--alpha",type=float,default=1/255)
    p.add_argument("--steps",type=int,default=10)
    p.add_argument("--block",type=int,default=8)
    p.add_argument("--batch-size",type=int,default=4)
    p.add_argument("--max-samples",type=int,default=0)
    p.add_argument("--seed",type=int,default=1024)
    p.add_argument("--expected-checkpoint-sha256",default=REFERENCE_SHA)
    return p.parse_args()

def auc(labels,scores):
    return float(roc_auc_score(labels,scores)) if set(labels)=={0,1} else None

def evaluation_summary(rows,method):
    if not rows:
        raise ValueError('Empty evaluation population')
    for row in rows:
        values=[row[k] for k in ('clean_score','attacked_score','linf','attention_mae','gates_mae')]
        if not np.isfinite(values).all():
            raise FloatingPointError('Non-finite per-frame metric')
    total_fake=[r for r in rows if r["label"]==1]
    clean_correct=[r for r in total_fake if r["clean_score"]>=.5]
    flipped=[r for r in clean_correct if r["attacked_score"]<.5]
    labels=[r["label"] for r in rows]
    clean=[r["clean_score"] for r in rows]
    attacked=[r["attacked_score"] for r in rows]
    mean_delta=float(np.mean([r["linf"] for r in rows])) if rows else None
    return {
        "method":method,"total_frames":len(rows),"fake_frames":len(total_fake),
        "eligible_clean_correct_fake":len(clean_correct),
        "fake_to_real_flips":len(flipped),
        "asr_fake_given_clean_correct":len(flipped)/len(clean_correct) if clean_correct else None,
        "unconditional_fake_evasion":sum(r["attacked_score"]<.5 for r in total_fake)/len(total_fake) if total_fake else None,
        "clean_frame_auc":auc(labels,clean),
        "attacked_fake_clean_real_frame_auc":auc(labels,attacked),
        "clean_frame_accuracy":float(np.mean([(s>=.5)==bool(y) for s,y in zip(clean,labels)])),
        "attacked_fake_clean_real_frame_accuracy":float(np.mean([(s>=.5)==bool(y) for s,y in zip(attacked,labels)])),
        "max_pixel_linf":max((r["linf"] for r in rows),default=None),
        "mean_pixel_linf":mean_delta,
        "attention_mae_mean":float(np.mean([r["attention_mae"] for r in total_fake])) if total_fake else None,
        "gates_mae_mean":float(np.mean([r["gates_mae"] for r in total_fake])) if total_fake else None
    }

def main():
    args=parse()
    if not 0<args.epsilon<=.2 or not 0<args.alpha<=.2 or args.steps<1 or args.batch_size<1:
        raise ValueError("Check epsilon, alpha, steps, and batch size")
    if args.block<2 or 256%args.block:
        raise ValueError("DCT block must divide input resolution 256")
    checkpoint_sha=file_sha256(args.checkpoint)
    if args.expected_checkpoint_sha256 and checkpoint_sha!=args.expected_checkpoint_sha256:
        raise ValueError("Unexpected checkpoint checksum; pass the correct reference explicitly")
    if not torch.cuda.is_available():raise RuntimeError("Real WGN evaluation requires CUDA")
    torch.manual_seed(args.seed);random.seed(args.seed);np.random.seed(args.seed)
    torch.backends.cudnn.benchmark=False
    source=args.repo_root/"experiments"/"EXP-002-WGN"/"reproduction"/"code"/"src"
    if not source.is_dir():raise FileNotFoundError(f"Missing original source {source}")
    sys.path.insert(0,str(source))
    from wgn.model import WaveletGuidedNetwork
    from wgn.data import FaceForensicsJsonDataset,build_records

    payload=torch.load(args.checkpoint,map_location="cpu",weights_only=False)
    config=payload["config"];cfg=config["model"];data_cfg=config["data"]
    model=WaveletGuidedNetwork(pretrained=False,backbone_name=cfg["backbone"],
                               gate_hidden_dim=cfg["gate_hidden_dim"]).cuda().eval()
    model.load_state_dict(payload["model"],strict=True)
    model.requires_grad_(False)
    records=build_records(json_path=args.manifest,data_root=args.data_root,split="test",
        frames_per_real=int(data_cfg["frames_per_real"]),
        frames_per_fake=int(data_cfg["frames_per_fake"]),
        manipulations=tuple(data_cfg["manipulations"]),compression=args.compression)
    indices=select_pilot(records,args.max_samples,args.seed)
    dataset=Subset(FaceForensicsJsonDataset(records,train=False),indices)
    batches=DataLoader(dataset,batch_size=args.batch_size,shuffle=False,num_workers=0)
    args.output.mkdir(parents=True,exist_ok=False)
    metadata={"experiment":"EXP-004-V2","reference":"Jia et al. CVPR 2022, Sec 3.1-3.2",
      "attack_status":{"fgsm":"standard baseline","pgd":"standard baseline",
                       "jia-faa-adapt":"documented methodological adaptation, NOT exact Jia reproduction"},
      "checkpoint_sha256":checkpoint_sha,"manifest_sha256":file_sha256(args.manifest),
      "source_dataset":"FaceForensics++ official test split","compression":args.compression,
      "preprocessing":"original EXP-002 WGN manifest + RGB resized to 256x256, no test augmentation",
      "methods":args.methods,"epsilon_pixel_linf":args.epsilon,"alpha":args.alpha,
      "steps":args.steps,"dct_block":args.block,"max_samples":args.max_samples,
      "selected_count":len(indices),"seed":args.seed,"device":torch.cuda.get_device_name(),
      "torch":torch.__version__,"python":platform.python_version(),
      "sampling":"test-only, deterministic, per-class/per-manipulation video round-robin",
      "attack_scope":"fake frames only; real test frames are held unchanged",
      "threshold_fake":0.5,
      "methodology_note":"pixel norm budget; differs from Jia Eq4 frequency-domain norm"}
    (args.output/"environment.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    hook=WGSADiagnostics(model)
    try:
        results={}
        for name in args.methods:
            records_out=[]
            for batch in batches:
                x=batch["image"].cuda(non_blocking=True)
                y=batch["label"].cuda(non_blocking=True)
                with torch.no_grad():
                    clean_logits=model(x); clean_score=clean_logits.sigmoid()
                    original=[{key:value[i:i+1].clone() for key,value in hook.current.items()}
                              for i in range(len(y))]
                adv=x.detach().clone()
                fake=(y==1)
                if fake.any():
                    with torch.enable_grad():
                        adv[fake]=attack(model,x[fake],name,args.epsilon,args.steps,args.alpha,args.block)
                with torch.no_grad():
                    logits=model(adv);scores=logits.sigmoid()
                    altered=[{key:value[i:i+1].clone() for key,value in hook.current.items()}
                              for i in range(len(y))]
                per_sample=(adv-x).abs().flatten(1).amax(1).cpu().tolist()
                if max(per_sample)>args.epsilon+1e-6:raise AssertionError("L-inf violation")
                for i in range(len(y)):
                    drift=compare_diagnostics(original[i],altered[i])
                    digest=hashlib.sha256(str(batch["path"][i]).encode()).hexdigest()[:16]
                    records_out.append({"record_id_sha256_16":digest,
                        "label":int(y[i]),"video":batch["video"][i],
                        "manipulation":batch["manipulation"][i],
                        "clean_score":float(clean_score[i]),
                        "attacked_score":float(scores[i]),"linf":float(per_sample[i]),
                        **drift})
            result=evaluation_summary(records_out,name)
            results[name]=result
            with (args.output/(name+"_per_frame.jsonl")).open("w",encoding="utf-8") as out:
                for record in records_out:out.write(json.dumps(record)+"\n")
            (args.output/(name+"_summary.json")).write_text(json.dumps(result,indent=2),encoding="utf-8")
            print(json.dumps(result),flush=True)
        (args.output/"results.json").write_text(json.dumps({"metadata":metadata,"results":results},indent=2),encoding="utf-8")
        print("EXP04_V2_COMPLETE "+str(args.output/"results.json"),flush=True)
    finally:hook.close()

if __name__=="__main__":main()
