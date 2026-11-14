import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
import torch
from paper_aligned_attacks import METHODS,attack,fusion_weight_from_clean_image
from attacks import block_transform

class TinyModel(torch.nn.Module):
    def forward(self,x):
        return 8*x.mean((1,2,3))-4

def test_dct_orthonormal_inverse():
    x=torch.rand(2,3,16,16)
    assert torch.allclose(block_transform(block_transform(x),inverse=True),x,atol=2e-6)

def test_attributed_attacks_bounded():
    torch.manual_seed(42)
    x=torch.rand(2,3,16,16)
    model=TinyModel()
    for name in METHODS:
        out=attack(model,x,name,epsilon=4/255,steps=2,alpha=1/255,block=8)
        assert out.shape==x.shape
        assert out.min()>=0 and out.max()<=1
        assert (out-x).abs().max()<=4/255+1e-6
        assert torch.isfinite(out).all()

def test_frequency_weight_shape_and_range():
    x=torch.rand(2,3,16,16)
    weight=fusion_weight_from_clean_image(x,block=8)
    assert weight.shape==x.shape
    assert float(weight.min())>=0.099999
    assert float(weight.max())<=1.000001

def test_fgsm_increases_fake_loss_in_easy_region():
    x=torch.full((1,3,16,16),0.8)
    model=TinyModel()
    out=attack(model,x,"fgsm",4/255,1,4/255,8)
    assert model(out).item()<model(x).item()
