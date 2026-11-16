"""CPU test: zero-initialized RCWG exactly matches reference WGSA."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import torch
from torch import nn
from torch.nn import functional as F
from reliability_wgsa import ReliabilityCalibratedWGSA

class RefWGSA(nn.Module):
    def __init__(self):
        super().__init__()
        self.eps=1e-6
        self.gate=nn.Sequential(nn.Linear(4,4),nn.ReLU(),nn.Linear(4,4),nn.Sigmoid())
        kernels=torch.tensor([[[1,1],[1,1]],[[1,-1],[1,-1]],[[1,1],[-1,-1]],[[1,-1],[-1,1]]],
                             dtype=torch.float32).unsqueeze(1)/2
        self.register_buffer("haar_kernels",kernels)
    def forward(self,x):
        guide=.5*(x.mean(1,keepdim=True)+x.amax(1,keepdim=True))
        bands=F.conv2d(guide,self.haar_kernels,stride=2)
        gates=self.gate(bands.mean((2,3)))
        raw=F.conv_transpose2d(bands*gates[:,:,None,None],self.haar_kernels,stride=2)
        attention=(raw-raw.amin((2,3),keepdim=True))/(raw.amax((2,3),keepdim=True)-raw.amin((2,3),keepdim=True)+self.eps)
        return x*attention,attention

def test_initial_identity_and_gradients():
    torch.manual_seed(4)
    ref=RefWGSA()
    candidate=ReliabilityCalibratedWGSA(ref)
    x=torch.randn(2,8,8,8)
    original=ref(x);modified=candidate(x)
    for a,b in zip(original,modified):
        assert torch.allclose(a,b,rtol=1e-6,atol=1e-6)
    modified[0].sum().backward()
    assert candidate.residual_scale.grad is not None
