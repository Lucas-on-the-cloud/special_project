"""Read-only Linux/Windows preflight; no downloading or GPU training."""
import argparse, hashlib, importlib, json, platform, sys
from pathlib import Path
parser=argparse.ArgumentParser()
for name in ("repo-root","checkpoint","manifest","data-root"):
    parser.add_argument("--"+name,type=Path,required=True)
a=parser.parse_args()
status={"python":platform.python_version(),"platform":platform.platform(),"paths":{},"packages":{}}
for key in ("repo_root","checkpoint","manifest","data_root"):
    value=getattr(a,key)
    status["paths"][key]={"path":str(value),"exists":value.exists()}
for name in ("torch","torchvision","timm","PIL","numpy","sklearn","yaml"):
    try:
        pkg=importlib.import_module(name)
        status["packages"][name]=getattr(pkg,"__version__","installed")
    except Exception as exc:
        status["packages"][name]="ERROR: "+str(exc)
try:
    import torch
    status["cuda_available"]=torch.cuda.is_available()
    status["gpu_name"]=torch.cuda.get_device_name() if status["cuda_available"] else None
except Exception:
    status["cuda_available"]=False
if a.checkpoint.is_file():
    h=hashlib.sha256()
    with a.checkpoint.open("rb") as f:
        for part in iter(lambda:f.read(1048576),b""):h.update(part)
    status["checkpoint_sha256"]=h.hexdigest()
print(json.dumps(status,indent=2))
if not all(v["exists"] for v in status["paths"].values()) or not status["cuda_available"] or any(str(v).startswith("ERROR") for v in status["packages"].values()):
    sys.exit("PREFLIGHT FAILED: resolve paths/packages/CUDA")
