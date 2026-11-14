import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
import torch
from attacks import block_transform,frequency_mask,build_attack

class ToyDetector(torch.nn.Module):
    def forward(self,x): return x.mean((1,2,3))*8-4

def test_dct_reconstruction():
    torch.manual_seed(7)
    x=torch.rand(2,3,16,24)
    y=block_transform(block_transform(x,8),8,inverse=True)
    assert torch.allclose(x,y,atol=2e-6)

def test_frequency_masks_partition():
    x=torch.zeros(1,3,16,16)
    masks=sum(frequency_mask(x,8,b) for b in ("low","mid","high"))
    assert torch.equal(masks,torch.ones_like(masks))

def test_attack_budgets():
    torch.manual_seed(2)
    model=ToyDetector();x=torch.rand(2,3,16,16);y=torch.tensor([0.,1.])
    for method in ("clean","fgsm","pgd","dct-low","dct-mid","dct-high","dct-all","hybrid","stat-proxy"):
        out=build_attack(method,model,x,y,eps=4/255,steps=2,step_size=1/255,block=8)
        assert out.shape==x.shape
        assert torch.isfinite(out).all()
        assert out.min()>=0 and out.max()<=1
        assert (out-x).abs().max().item()<=4/255+1e-6,method
