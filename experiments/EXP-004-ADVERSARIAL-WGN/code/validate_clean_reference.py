"""Validate the restored EXP-002 checkpoint/data before any EXP-004 attack.

The gate is deliberately strict: if the clean FF++ c23 result no longer matches
the frozen EXP-002 reference within tolerance, do not interpret adversarial
results. This script performs inference only; it never trains or mutates weights.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
import numpy as np
import torch
from sklearn.metrics import accuracy_score,roc_auc_score
from torch.utils.data import DataLoader

EXPECTED_SHA="a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6"
EXPECTED_FRAMES=11200
EXPECTED_ACC=0.9391964285714286
EXPECTED_AUC=0.9821176020408163

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):h.update(block)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    for name in ("repo-root","checkpoint","manifest","data-root","output"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--batch-size",type=int,default=32)
    p.add_argument("--tolerance",type=float,default=1e-3,
                   help="Absolute tolerance for ACC/AUC; 1e-3 = 0.1 percentage point")
    a=p.parse_args()
    if not torch.cuda.is_available():raise RuntimeError("CUDA required")
    if sha256(a.checkpoint)!=EXPECTED_SHA:raise RuntimeError("EXP-002 checkpoint SHA mismatch")
    src=a.repo_root/"experiments"/"EXP-002-WGN"/"reproduction"/"code"/"src"
    sys.path.insert(0,str(src))
    from wgn.model import WaveletGuidedNetwork
    from wgn.data import FaceForensicsJsonDataset,build_records
    payload=torch.load(a.checkpoint,map_location="cpu",weights_only=False)
    cfg=payload["config"]; model_cfg=cfg["model"]; data_cfg=cfg["data"]
    model=WaveletGuidedNetwork(pretrained=False,backbone_name=model_cfg["backbone"],
                               gate_hidden_dim=model_cfg["gate_hidden_dim"]).cuda().eval()
    model.load_state_dict(payload["model"],strict=True)
    model.requires_grad_(False)
    records=build_records(a.manifest,a.data_root,"test",
        int(data_cfg["frames_per_real"]),int(data_cfg["frames_per_fake"]),
        tuple(data_cfg["manipulations"]),"c23")
    if len(records)!=EXPECTED_FRAMES:
        raise RuntimeError(f"Expected {EXPECTED_FRAMES} FF++ c23 test frames, got {len(records)}")
    loader=DataLoader(FaceForensicsJsonDataset(records,train=False),batch_size=a.batch_size,
                      shuffle=False,num_workers=0)
    labels=[];scores=[]
    with torch.no_grad():
        for batch in loader:
            logits=model(batch["image"].cuda(non_blocking=True))
            labels.extend(batch["label"].int().tolist())
            scores.extend(logits.sigmoid().cpu().tolist())
    labels=np.asarray(labels);scores=np.asarray(scores)
    acc=float(accuracy_score(labels,scores>=.5));auc=float(roc_auc_score(labels,scores))
    result={"frames":len(labels),"accuracy":acc,"auc":auc,
            "expected_accuracy":EXPECTED_ACC,"expected_auc":EXPECTED_AUC,
            "accuracy_abs_diff":abs(acc-EXPECTED_ACC),"auc_abs_diff":abs(auc-EXPECTED_AUC),
            "tolerance":a.tolerance,"checkpoint_sha256":EXPECTED_SHA,
            "manifest_sha256":sha256(a.manifest)}
    passed=result["accuracy_abs_diff"]<=a.tolerance and result["auc_abs_diff"]<=a.tolerance
    result["passed"]=passed
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    if not passed:
        raise SystemExit("CLEAN_REFERENCE_GATE_FAILED: debug data/model/environment before EXP-004")

if __name__=="__main__":main()
