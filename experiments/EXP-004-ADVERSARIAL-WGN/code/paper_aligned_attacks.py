"""EXP-004 V2. Explicitly attributed adversarial evaluation algorithms.

FGSM and pixel PGD implement the well-defined first-order baselines in
Jia et al. CVPR 2022 Sec.3.1, eqs. (2) and (3) (standard algorithms).
JIA_FAA_ADAPT is a TRANSPARENT operational adaptation of Jia et al.
Sec.3.2, eqs. (4)-(7), Algorithm 1. The paper omits an executable
specification for the dynamic frequency-fusion matrix M; here M is a
declared deterministic function of clean-image block-DCT magnitude.
DO NOT report JIA_FAA_ADAPT as original-author reproducibility.
"""
from __future__ import annotations
import torch
import torch.nn.functional as F
from attacks import block_transform

def clamp_box_and_linf(candidate, reference, epsilon):
    """Pixel-domain perturbation budget, RGB values in [0,1]."""
    return torch.maximum(torch.minimum(candidate,reference+epsilon),reference-epsilon).clamp(0,1)

def loss_fake_to_real(model,images):
    """Maximize BCE with y=1 for fake inputs (reduces fake logit)."""
    return F.binary_cross_entropy_with_logits(
        model(images).reshape(-1),torch.ones(images.size(0),device=images.device))

def fgsm_jia_reference(model, x, epsilon):
    x=x.detach()
    variable=x.clone().requires_grad_(True)
    grad=torch.autograd.grad(loss_fake_to_real(model,variable),variable)[0]
    return clamp_box_and_linf(x+epsilon*grad.sign(),x,epsilon).detach()

def pgd_jia_reference(model, x, epsilon, steps, alpha, *, random_start=False):
    x=x.detach()
    adv=(x+torch.empty_like(x).uniform_(-epsilon,epsilon)).clamp(0,1) if random_start else x.clone()
    for _ in range(steps):
        var=adv.detach().requires_grad_(True)
        grad=torch.autograd.grad(loss_fake_to_real(model,var),var)[0]
        adv=clamp_box_and_linf(var.detach()+alpha*grad.sign(),x,epsilon)
    return adv.detach()

def fusion_weight_from_clean_image(x,block=8,floor=.10):
    """Declared substitute for Jia's unspecified dynamic M.

    For each sample, channel, and DCT coefficient position, average
    |DCT(x)| across spatial blocks and normalize by the largest average.
    Floor prevents degeneracy. Expanded across blocks, detached from x.
    This is NOT asserted to match the authors' M construction.
    """
    b,c,h,w=x.shape
    if h%block or w%block:raise ValueError("Image size not divisible by block")
    coeff=block_transform(x.detach(),block)
    band=coeff.reshape(b,c,h//block,block,w//block,block)
    band=band.permute(0,1,2,4,3,5).abs().mean((2,3))
    band=band/(band.amax((2,3),keepdim=True)+1e-8)
    m=floor+(1-floor)*band
    return m[:, :, None,None,:,:].expand(-1,-1,h//block,w//block,-1,-1).permute(0,1,2,4,3,5).reshape(b,c,h,w).detach()

def jia_faa_adaptation(model,x,epsilon,steps,alpha,*,block=8,m_floor=.10):
    """Jia Algorithm-1 structured adaptation, with explicitly specified M.

    Initialize P~U(0,1), optimize sign gradient through IDCT(DCT(x_adv)+M*P),
    reconstruct with IDCT and project to a *pixel* Linf epsilon ball.
    Unlike paper Eq.(4), this evaluation uses a pixel-space budget to
    permit direct comparison against FGSM/PGD. See PROTOCOL.md.
    """
    x=x.detach()
    m=fusion_weight_from_clean_image(x,block,m_floor)
    perturb=torch.rand_like(x)*alpha
    adv=x.clone()
    for _ in range(steps):
        p=perturb.detach().requires_grad_(True)
        transformed=block_transform(adv.detach(),block)
        candidate=clamp_box_and_linf(block_transform(transformed+m*p,block,inverse=True),x,epsilon)
        grad=torch.autograd.grad(loss_fake_to_real(model,candidate),p)[0]
        perturb=(p.detach()+alpha*grad.sign())
        transformed=block_transform(adv.detach(),block)
        adv=clamp_box_and_linf(block_transform(transformed+m*perturb,block,inverse=True),x,epsilon).detach()
    return adv.detach()

METHODS=("fgsm","pgd","jia-faa-adapt")
def attack(model,images,name,epsilon,steps,alpha,block=8):
    if name=="fgsm":return fgsm_jia_reference(model,images,epsilon)
    if name=="pgd":return pgd_jia_reference(model,images,epsilon,steps,alpha)
    if name=="jia-faa-adapt":return jia_faa_adaptation(model,images,epsilon,steps,alpha,block=block)
    raise ValueError(f"Unknown paper-aligned method {name}")
