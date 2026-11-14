"""EXP-004: attack frozen reproduced WGN; measure ASR, AUC and WGSA drift."""
from __future__ import annotations
import argparse,hashlib,json,platform,random,sys
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader,Subset
from attacks import build_attack
from diagnostics import WGSADiagnostics,compare_diagnostics

def parse():
    p=argparse.ArgumentParser()
    for key in ("repo-root","checkpoint","manifest","data-root","output"):
        p.add_argument("--"+key,type=Path,required=True)
    p.add_argument("--compression",default="c23",choices=["c23","c40"])
    p.add_argument("--attacks",nargs="+",default=["clean","fgsm","pgd","dct-low","dct-mid","dct-high","dct-all","hybrid","stat-proxy"])
    p.add_argument("--eps",type=float,default=4/255)
    p.add_argument("--steps",type=int,default=10)
    p.add_argument("--step-size",type=float,default=1/255)
    p.add_argument("--batch-size",type=int,default=8)
    p.add_argument("--max-samples",type=int,default=0)
    p.add_argument("--seed",type=int,default=1024)
    p.add_argument("--block",type=int,default=8)
    p.add_argument("--expected-sha256",default="")
    return p.parse_args()

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for part in iter(lambda:f.read(1048576),b""):h.update(part)
    return h.hexdigest()

def auc(y,p):
    return float(roc_auc_score(y,p)) if len(set(y))==2 else None

def main():
    a=parse()
    if not 0<a.eps<=.25 or a.steps<1 or a.step_size<=0 or a.batch_size<1:
        raise ValueError("Invalid attack parameters")
    if not a.checkpoint.is_file() or not a.manifest.is_file():
        raise FileNotFoundError("Missing checkpoint or manifest")
    checksum=sha(a.checkpoint)
    if a.expected_sha256 and checksum.lower()!=a.expected_sha256.lower():
        raise RuntimeError("Checkpoint SHA-256 mismatch")
    if not torch.cuda.is_available(): raise RuntimeError("CUDA required for real WGN evaluation")
    random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed);torch.cuda.manual_seed_all(a.seed)
    source=a.repo_root/"experiments"/"EXP-002-WGN"/"reproduction"/"code"/"src"
    if not source.is_dir(): raise FileNotFoundError(str(source))
    sys.path.insert(0,str(source))
    from wgn.model import WaveletGuidedNetwork
    from wgn.data import FaceForensicsJsonDataset,build_records
    checkpoint=torch.load(a.checkpoint,map_location="cpu",weights_only=False)
    config=checkpoint.get("config",{})
    settings=config.get("model",{})
    model=WaveletGuidedNetwork(pretrained=False,
        backbone_name=settings.get("backbone","mobilevit_s.cvnets_in1k"),
        gate_hidden_dim=int(settings.get("gate_hidden_dim",4))).cuda().eval()
    model.load_state_dict(checkpoint["model"],strict=True)
    for param in model.parameters(): param.requires_grad_(False)
    data_cfg=config.get("data",{})
    records=build_records(a.manifest,a.data_root,"test",
        frames_per_real=int(data_cfg.get("frames_per_real",40)),
        frames_per_fake=int(data_cfg.get("frames_per_fake",10)),
        manipulations=tuple(data_cfg.get("manipulations",("FF-DF","FF-F2F","FF-FS","FF-NT"))),
        compression=a.compression)
    dataset=FaceForensicsJsonDataset(records,train=False)
    if a.max_samples:
        by_label={0:[],1:[]}
        for i,record in enumerate(records): by_label[record.label].append(i)
        per_class=max(1,a.max_samples//2)
        dataset=Subset(dataset,sorted(by_label[0][:per_class]+by_label[1][:per_class]))
    loader=DataLoader(dataset,batch_size=a.batch_size,shuffle=False,num_workers=0)
    a.output.mkdir(parents=True,exist_ok=True)
    if (a.output/"results.json").exists(): raise FileExistsError("Choose new output directory")
    meta={"checkpoint_sha256":checksum,"manifest_sha256":sha(a.manifest),
          "checkpoint":str(a.checkpoint),"compression":a.compression,"attacks":a.attacks,
          "eps_pixel_linf":a.eps,"steps":a.steps,"step_size":a.step_size,"seed":a.seed,
          "block_dct":a.block,"num_samples":len(dataset),"torch":torch.__version__,
          "cuda":torch.version.cuda,"device":torch.cuda.get_device_name(),
          "python":platform.python_version(),"attack_scope":"all real and fake images",
          "attack_type":"untargeted white-box BCE maximization",
          "not_exact_reproduction":["Jia frequency attack","Jia hybrid","Hou StatAttack"]}
    (a.output/"environment.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    capture=WGSADiagnostics(model)
    try:
        results={}
        for attack in a.attacks:
            labels=[];probs=[];clean_probs=[];distort=[];drift=[]
            eligible_count=0;evasion_count=0
            for idx,batch in enumerate(loader):
                x=batch["image"].cuda();y=batch["label"].cuda()
                with torch.no_grad():
                    clean_logits=model(x)
                    clean_diag=capture.current
                    clean_score=clean_logits.sigmoid()
                with torch.enable_grad():
                    adversarial=build_attack(attack,model,x,y,a.eps,a.steps,a.step_size,a.block)
                with torch.no_grad():
                    logits=model(adversarial);attack_diag=capture.current
                    score=logits.sigmoid()
                labels.extend(y.cpu().int().tolist())
                probs.extend(score.cpu().tolist())
                clean_probs.extend(clean_score.cpu().tolist())
                delta=(adversarial-x).abs().flatten(1).amax(1)
                if float(delta.max())>a.eps+1e-5: raise AssertionError("L-inf budget exceeded")
                distort.extend(delta.cpu().tolist())
                drift.append(compare_diagnostics(clean_diag,attack_diag))
                eligible=(y==1)&(clean_score>=.5)
                eligible_count+=int(eligible.sum())
                evasion_count+=int((eligible&(score<.5)).sum())
                print(json.dumps({"attack":attack,"batch":idx+1,"samples":len(labels)}),flush=True)
            yy=np.asarray(labels);pp=np.asarray(probs)
            results[attack]={"samples":len(labels),"clean_auc_same_samples":auc(labels,clean_probs),
                "attacked_auc":auc(labels,probs),"attacked_accuracy":float(((pp>=.5)==yy).mean()),
                "fake_evasion_asr_given_clean_correct":evasion_count/eligible_count if eligible_count else None,
                "fake_eligible_clean_correct":eligible_count,"max_pixel_linf":max(distort),
                "mean_drift":{k:float(np.mean([d[k] for d in drift])) for k in drift[0]}}
            (a.output/(attack+".json")).write_text(json.dumps(results[attack],indent=2),encoding="utf-8")
        (a.output/"results.json").write_text(json.dumps({"metadata":meta,"results":results},indent=2),encoding="utf-8")
        print("EXP04_COMPLETE "+str(a.output/"results.json"),flush=True)
    finally:
        capture.close()

if __name__=="__main__":
    main()
