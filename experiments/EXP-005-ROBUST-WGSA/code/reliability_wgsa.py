"""EXP-005 PROTOTYPE: Reliability-Calibrated Wavelet Gating (RCWG).

Hypothesis only. Not validated and not a certified or claimed novel defense.
Drop-in WGSA replacement that preserves reference weights at initialization.
"""
from __future__ import annotations
import torch
from torch import nn
import torch.nn.functional as F

class ReliabilityCalibratedWGSA(nn.Module):
    def __init__(self,reference_wgsa,hidden=16):
        super().__init__()
        self.eps=reference_wgsa.eps
        self.gate=reference_wgsa.gate
        self.register_buffer("haar_kernels",reference_wgsa.haar_kernels.detach().clone())
        self.reliability=nn.Sequential(nn.Linear(16,hidden),nn.GELU(),nn.Linear(hidden,4))
        self.residual_scale=nn.Parameter(torch.zeros(()))
        self.last_diagnostics=None

    def forward(self,features):
        guide=.5*(features.mean(1,keepdim=True)+features.amax(1,keepdim=True))
        bands=F.conv2d(guide,self.haar_kernels,stride=2)
        signed=bands.mean((2,3))
        magnitude=bands.abs().mean((2,3))
        variance=bands.var((2,3),unbiased=False)
        energy=bands.square().mean((2,3))
        relative_energy=energy/(energy.sum(dim=1,keepdim=True)+self.eps)
        descriptor=torch.cat([signed,magnitude,variance,relative_energy],dim=1)
        reliability=torch.sigmoid(self.reliability(descriptor))
        original_gates=self.gate(signed)
        scale=.5*torch.tanh(self.residual_scale)
        calibrated=original_gates*(1+scale*(2*reliability-1))
        weighted=bands*calibrated[:,:,None,None]
        raw=F.conv_transpose2d(weighted,self.haar_kernels,stride=2)
        amin=raw.amin((2,3),keepdim=True)
        amax=raw.amax((2,3),keepdim=True)
        attention=(raw-amin)/(amax-amin+self.eps)
        self.last_diagnostics={"reliability":reliability.detach(),
                               "gates":calibrated.detach(),"scale":scale.detach()}
        return features*attention,attention

def attach_to_wgn(model,hidden=16):
    """Call only after strict loading of original WGN checkpoint."""
    model.wgsa=ReliabilityCalibratedWGSA(model.wgsa,hidden=hidden)
    return model

def paired_robustness_loss(clean_logits,attacked_logits,labels,lambda_consistency=0.1):
    """Illustrative loss; adaptive inner maximization must be implemented separately."""
    clean=F.binary_cross_entropy_with_logits(clean_logits,labels)
    attacked=F.binary_cross_entropy_with_logits(attacked_logits,labels)
    consistency=F.mse_loss(clean_logits.sigmoid(),attacked_logits.sigmoid())
    return .5*(clean+attacked)+lambda_consistency*consistency
