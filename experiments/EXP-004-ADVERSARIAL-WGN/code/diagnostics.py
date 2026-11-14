"""Non-invasive forward-hook captures for original WGSA."""
from __future__ import annotations
import torch
from torch.nn import functional as F

class WGSADiagnostics:
    def __init__(self,model):
        if not hasattr(model,"wgsa"): raise ValueError("Expected model.wgsa")
        self.module=model.wgsa
        self.current=None
        self.handle=self.module.register_forward_hook(self._hook)
    def _hook(self,module,inputs,outputs):
        with torch.no_grad():
            features=inputs[0].detach()
            guide=.5*(features.mean(1,keepdim=True)+features.amax(1,keepdim=True))
            bands=F.conv2d(guide,module.haar_kernels,stride=2)
            means=bands.mean((2,3))
            self.current={"mean":means.cpu(),"abs_mean":bands.abs().mean((2,3)).cpu(),
                          "energy":bands.square().mean((2,3)).cpu(),"gates":module.gate(means).cpu(),
                          "attention":outputs[1].detach().cpu()}
    def close(self): self.handle.remove()

def compare_diagnostics(clean,adversarial):
    return {name+"_mae":float((clean[name]-adversarial[name]).abs().mean())
            for name in ("mean","abs_mean","energy","gates","attention")}
