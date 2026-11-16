"""Declared Hou/WGN adaptation, not exact author experiment reproduction.

Source-consistent StatAttack operators/MMD/momentum with 40 paper-derived
updates. MStatAttack is an explicit three-layer reconstruction. See the locked
profile and HOU-ALGORITHM-SPEC.md for every deviation and feasibility choice.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import math

import torch
from torch.nn import functional as F


@dataclass(frozen=True)
class AttackConfig:
    steps: int = 40
    degree: int = 11
    tune_scale: int = 8
    kernel: int = 3
    total_epsilon: float = 60/255
    noise_epsilon: float = 4/255
    exposure_lr: float = .1
    flow_lr: float = .001
    noise_lr: float = 1/255
    blur_lr: float = .1
    mixture_lr: float = .1
    lambda_mmd: float = 10.
    lambda_bias: float = 10.
    lambda_flow: float = 10.
    momentum: float = 1.
    exposure_log_limit: float = 20.
    bandwidth_floor: float = 1e-12
    layers: int = 3

    def validate(self):
        if self.steps<0 or self.degree<1 or self.tune_scale<1 or self.kernel<1 or self.kernel%2!=1 or self.layers<1:
            raise ValueError('Invalid transform/iteration setting')
        values=asdict(self)
        if not all(math.isfinite(v) for v in values.values()) or min(values.values())<0:
            raise ValueError('Nonfinite/negative setting')
        if min(self.total_epsilon,self.noise_epsilon,self.lambda_mmd,self.exposure_log_limit,self.bandwidth_floor)<=0:
            raise ValueError('Budgets/MMD/numerical limits must be positive')


def finite(x, name):
    if not torch.isfinite(x).all():
        raise FloatingPointError('Nonfinite '+name)
    return x


def mmd(source, target, floor=1e-12):
    """Biased five-RBF MMD, detached empirical bandwidth, equal batches."""
    if source.ndim!=2 or source.shape!=target.shape or not len(source):
        raise ValueError('Expected equal nonempty N x D feature batches')
    finite(source,'source features');finite(target,'reference features')
    total=torch.cat((source,target),0)
    distance=(total[:,None,:]-total[None,:,:]).square().sum(-1)
    n=len(total)
    bandwidth=(distance.detach().sum()/(n*n-n)).clamp_min(floor)
    kernels=sum(torch.exp(-distance/(bandwidth*(2.**(i-2)))) for i in range(5))
    b=len(source)
    return finite(kernels[:b,:b].mean()+kernels[b:,b:].mean()
                  -kernels[:b,b:].mean()-kernels[b:,:b].mean(),'MMD')


def polynomial_basis(x,degree):
    h,w=x.shape[-2:]
    xx=torch.linspace(-1,1,w,device=x.device,dtype=x.dtype)[None,:].expand(h,w)
    yy=torch.linspace(-1,1,h,device=x.device,dtype=x.dtype)[:,None].expand(h,w)
    basis=torch.stack([xx**i*yy**j for i in range(degree+1) for j in range(degree-i+1)])
    coordinates=torch.stack((xx,yy),-1)
    return basis,coordinates


def exposure(x, coefficients, flow, basis, coordinates, log_limit):
    field=torch.einsum('ncd,dhw->nchw',coefficients,basis)
    up=F.interpolate(flow.permute(0,3,1,2),size=x.shape[-2:],mode='bilinear',align_corners=False)
    grid=(coordinates[None]+up.permute(0,2,3,1)).clamp(-1,1)
    field=F.grid_sample(field,grid,align_corners=True)
    # x*exp(field) is exp(log(x)+field) continued to x=0, without log(0).
    return x*field.clamp(-log_limit,log_limit).exp(),field


def adaptive_blur(x, precision, kernel):
    """Same normalized precision-squared exponent as the reviewed source."""
    radius=kernel//2
    if radius>=min(x.shape[-2:]):raise ValueError('Blur kernel exceeds image')
    offsets=torch.arange(-radius,radius+1,device=x.device,dtype=x.dtype)
    distance=(offsets[:,None].square()+offsets[None,:].square()).flatten()
    weights=(-.5*distance[None,None,:,None,None]*precision[:,:,None].square()).softmax(2)
    padded=F.pad(x,(radius,)*4,mode='reflect') if radius else x
    n,c,h,w=x.shape
    patches=F.unfold(padded,kernel_size=kernel).reshape(n,c,kernel*kernel,h,w)
    return (patches*weights).sum(2)


def feasible(x, clean, epsilon):
    return torch.maximum(torch.minimum(x,clean+epsilon),clean-epsilon).clamp(0,1)


def reference_indices(offset,count,bank_size):
    if min(count,bank_size)<1 or offset<0:raise ValueError('Invalid reference assignment')
    return [(offset+i)%bank_size for i in range(count)]


def attack(feature_fn, clean, reference_features, config, *, multilayer=False, initialize_only=False):
    config.validate()
    if clean.ndim!=4 or clean.shape[1]!=3 or not len(clean):raise ValueError('Expected nonempty RGB BCHW')
    finite(clean,'clean RGB')
    if clean.min()<0 or clean.max()>1:raise ValueError('RGB outside [0,1]')
    if len(reference_features)!=len(clean) or reference_features.requires_grad:
        raise ValueError('Equal detached reference batch required')
    clean=clean.detach()
    n,c,h,w=clean.shape
    if min(h,w)<config.tune_scale:raise ValueError('Flow grid too small')
    basis,coordinates=polynomial_basis(clean,config.degree)
    count=config.layers if multilayer else 1
    layers=[];parameters=[];rates=[]
    for _ in range(count):
        coef=clean.new_zeros(n,1,len(basis)).requires_grad_()
        flow=clean.new_zeros(n,h//config.tune_scale,w//config.tune_scale,2).requires_grad_()
        precision=torch.full_like(clean,100/math.sqrt(c*h*w)).requires_grad_()
        noise=torch.zeros_like(clean).requires_grad_()
        params=[coef,flow,precision,noise]
        lrs=[config.exposure_lr,config.flow_lr,config.blur_lr,config.noise_lr]
        logits=clean.new_zeros(n,4).requires_grad_() if multilayer else None
        if multilayer:params.append(logits);lrs.append(config.mixture_lr)
        layers.append((coef,flow,precision,noise,logits))
        parameters.extend(params);rates.extend(lrs)

    def render():
        current=clean
        bias_penalty=clean.new_zeros(())
        flow_penalty=clean.new_zeros(())
        for coef,flow,precision,noise,logits in layers:
            exposed,field=exposure(current,coef,flow,basis,coordinates,config.exposure_log_limit)
            if multilayer:
                branches=torch.stack((exposed,adaptive_blur(current,precision,config.kernel),current+noise,current),1)
                current=(branches*logits.softmax(1)[:,:,None,None,None]).sum(1)
            else:
                current=adaptive_blur(exposed,precision,config.kernel)+noise
            # Shared clean-origin bound after every layer is a declared project choice.
            current=feasible(current,clean,config.total_epsilon)
            bias_penalty=bias_penalty+field.square().sum()/(h*w)
            flow_penalty=flow_penalty+(flow[:,:,1:,:]-flow[:,:,:-1,:]).square().sum()/config.tune_scale**2
            flow_penalty=flow_penalty+(flow[:,1:,:,:]-flow[:,:-1,:,:]).square().sum()/config.tune_scale**2
        return finite(current,'rendered RGB'),bias_penalty/count,flow_penalty/count

    trace=[];momentum=None
    updates=0 if initialize_only else config.steps
    with torch.no_grad():clean_mmd=float(mmd(feature_fn(clean),reference_features,config.bandwidth_floor))
    for iteration in range(updates+1):
        output,bias_penalty,flow_penalty=render()
        value=mmd(feature_fn(output),reference_features,config.bandwidth_floor)
        loss=finite(config.lambda_mmd*value+config.lambda_bias*bias_penalty+config.lambda_flow*flow_penalty,'objective')
        if iteration==0 or iteration==updates or iteration%10==0:
            trace.append(dict(update=iteration,mmd=float(value.detach()),objective=float(loss.detach()),
                bias_penalty=float(bias_penalty.detach()),flow_penalty=float(flow_penalty.detach())))
        if iteration==updates:break
        gradients=torch.autograd.grad(loss,parameters)
        with torch.no_grad():
            normalized=[]
            for gradient in gradients:
                finite(gradient,'parameter gradient')
                norm=gradient.flatten(1).abs().sum(1)
                norm=torch.where(norm>0,norm,torch.ones_like(norm))
                normalized.append(gradient/norm.reshape(-1,*([1]*(gradient.ndim-1))))
            momentum=normalized if momentum is None else [config.momentum*old+new for old,new in zip(momentum,normalized)]
            for parameter,gradient,rate in zip(parameters,momentum,rates):parameter.add_(gradient.sign(),alpha=-rate)
            for _,_,_,noise,_ in layers:noise.clamp_(-config.noise_epsilon,config.noise_epsilon)
    output=output.detach()
    if (output-clean).abs().max()>config.total_epsilon+1e-6:raise AssertionError('Total RGB budget exceeded')
    details={'updates':updates,'clean_mmd':clean_mmd,'trace':trace,
             'mixture_weights':[p[4].detach().softmax(1).cpu().tolist() for p in layers] if multilayer else None,
             'max_noise':max(float(p[3].detach().abs().max()) for p in layers)}
    return output,details
