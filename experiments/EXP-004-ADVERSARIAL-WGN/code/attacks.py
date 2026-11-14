"""Bounded first-order attacks for offline robustness research.
Jia/Hou-inspired probes, not faithful reproductions of their full methods.
Inputs are [0,1] RGB tensors. All outputs obey a pixel L-infinity budget.
"""
from __future__ import annotations
import math
import torch
from torch.nn import functional as F

def project(x, original, eps):
    return torch.maximum(torch.minimum(x, original + eps), original - eps).clamp(0,1)

def dct_matrix(n, device, dtype):
    i=torch.arange(n,device=device,dtype=dtype)
    k=torch.arange(n,device=device,dtype=dtype)[:,None]
    m=torch.cos(math.pi*(i[None,:]+.5)*k/n)*math.sqrt(2/n)
    m[0]/=math.sqrt(2)
    return m

def block_transform(x,size=8,inverse=False):
    b,c,h,w=x.shape
    if h%size or w%size: raise ValueError("Image dimensions must be divisible by DCT block size")
    m=dct_matrix(size,x.device,x.dtype)
    blocks=x.reshape(b,c,h//size,size,w//size,size).permute(0,1,2,4,3,5)
    left,right=(m.T,m) if inverse else (m,m.T)
    out=torch.matmul(torch.matmul(left,blocks),right)
    return out.permute(0,1,2,4,3,5).contiguous().reshape(b,c,h,w)

def frequency_mask(x,size=8,band="all"):
    _,_,h,w=x.shape
    if h%size or w%size: raise ValueError("Invalid DCT block size")
    i=torch.arange(size,device=x.device)
    radius=i[:,None]+i[None,:]
    if band=="low": mask=radius<=size//2
    elif band=="mid": mask=(radius>size//2)&(radius<=size)
    elif band=="high": mask=radius>size
    elif band=="all": mask=torch.ones_like(radius,dtype=torch.bool)
    else: raise ValueError(f"Unknown band: {band}")
    return mask.to(x.dtype).repeat(h//size,w//size)[None,None]

def objective(model,x,y):
    return F.binary_cross_entropy_with_logits(model(x).reshape(-1),y.reshape(-1))

def pixel_pgd(model,x,y,eps=4/255,steps=10,step=1/255,random_start=False):
    original=x.detach()
    adv=project(original+torch.empty_like(original).uniform_(-eps,eps),original,eps) if random_start else original.clone()
    for _ in range(steps):
        adv=adv.detach().requires_grad_(True)
        grad=torch.autograd.grad(objective(model,adv,y),adv)[0]
        adv=project(adv.detach()+step*grad.sign(),original,eps)
    return adv.detach()

def pixel_fgsm(model,x,y,eps=4/255):
    return pixel_pgd(model,x,y,eps,steps=1,step=eps)

def dct_pgd(model,x,y,eps=4/255,steps=10,step=1/255,band="all",block=8,random_start=False):
    """Projection may introduce out-of-band energy in the final pixel image."""
    original=x.detach()
    mask=frequency_mask(original,block,band)
    coeff=torch.zeros_like(original)
    if random_start:
        coeff=block_transform(torch.empty_like(original).uniform_(-eps,eps),block)*mask
    for _ in range(steps):
        coeff=coeff.detach().requires_grad_(True)
        adv=project(original+block_transform(coeff*mask,block,True),original,eps)
        grad=torch.autograd.grad(objective(model,adv,y),coeff)[0]
        coeff=(coeff.detach()+step*(grad*mask).sign())*mask
        candidate=project(original+block_transform(coeff,block,True),original,eps)
        coeff=block_transform(candidate-original,block)*mask
    return project(original+block_transform(coeff,block,True),original,eps).detach()

def hybrid_pgd(model,x,y,eps=4/255,steps=10,step=1/255,block=8):
    """Alternating pixel/DCT gradient steps, not Jia meta-learning reproduction."""
    original=x.detach();adv=original.clone()
    for i in range(steps):
        if i%2==0:
            adv=adv.detach().requires_grad_(True)
            grad=torch.autograd.grad(objective(model,adv,y),adv)[0]
            adv=project(adv.detach()+step*grad.sign(),original,eps)
        else:
            coeff=block_transform(adv.detach(),block).requires_grad_(True)
            image=project(block_transform(coeff,block,True),original,eps)
            grad=torch.autograd.grad(objective(model,image,y),coeff)[0]
            adv=project(block_transform(coeff.detach()+step*grad.sign(),block,True),original,eps)
    return adv.detach()

def statistical_proxy(model,x,y,eps=4/255,steps=10,step=1/255):
    """Exposure/blur/low-res-noise diagnostic; NOT Hou StatAttack/MStatAttack."""
    base=x.detach()
    smooth=F.avg_pool2d(F.pad(base,(1,1,1,1),mode="reflect"),3,stride=1)
    b,c,h,w=base.shape
    exposure=torch.zeros((b,1,1,1),device=base.device,dtype=base.dtype)
    blur=exposure.clone()
    noise=torch.zeros((b,c,max(1,h//32),max(1,w//32)),device=base.device,dtype=base.dtype)
    for _ in range(steps):
        exposure=exposure.detach().requires_grad_(True)
        blur=blur.detach().requires_grad_(True)
        noise=noise.detach().requires_grad_(True)
        up=F.interpolate(noise,size=(h,w),mode="bilinear",align_corners=False)
        adv=project(base+exposure*(base-.5)+blur*(smooth-base)+up,base,eps)
        grads=torch.autograd.grad(objective(model,adv,y),(exposure,blur,noise))
        exposure=(exposure.detach()+step*grads[0].sign()).clamp(-.2,.2)
        blur=(blur.detach()+step*grads[1].sign()).clamp(0,1)
        noise=(noise.detach()+step*grads[2].sign()).clamp(-eps,eps)
    up=F.interpolate(noise,size=(h,w),mode="bilinear",align_corners=False)
    return project(base+exposure*(base-.5)+blur*(smooth-base)+up,base,eps).detach()

def build_attack(name,model,image,label,eps,steps,step_size,block=8):
    if name=="clean": return image.detach()
    if name=="fgsm": return pixel_fgsm(model,image,label,eps)
    if name=="pgd": return pixel_pgd(model,image,label,eps,steps,step_size)
    if name=="stat-proxy": return statistical_proxy(model,image,label,eps,steps,step_size)
    if name=="hybrid": return hybrid_pgd(model,image,label,eps,steps,step_size,block)
    if name.startswith("dct-"): return dct_pgd(model,image,label,eps,steps,step_size,name[4:],block)
    raise ValueError(f"Unsupported attack: {name}")
