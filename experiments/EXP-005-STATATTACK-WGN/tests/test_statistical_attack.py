import copy
from dataclasses import replace
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy.ndimage import correlate
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from statistical_attack import AttackConfig,mmd,exposure,polynomial_basis,adaptive_blur,attack,reference_indices


def test_mmd_matches_independent_numpy_and_permutation():
 x=np.array([[.1,.7],[.3,.2],[.6,.9]],dtype=np.float64)
 y=np.array([[.9,.4],[.2,.8],[.4,.4]],dtype=np.float64)
 z=np.concatenate((x,y));distance=np.square(z[:,None]-z[None,:]).sum(-1)
 bandwidth=distance.sum()/(len(z)**2-len(z))
 k=sum(np.exp(-distance/(bandwidth*2.**(i-2))) for i in range(5))
 expected=k[:3,:3].mean()+k[3:,3:].mean()-k[:3,3:].mean()-k[3:,:3].mean()
 source=torch.tensor(x,requires_grad=True);target=torch.tensor(y)
 value=mmd(source,target)
 assert float(value)==pytest.approx(expected,abs=1e-12)
 assert float(mmd(source,target[[2,0,1]]))==pytest.approx(expected,abs=1e-12)
 value.backward();assert source.grad.abs().sum()>0 and torch.isfinite(source.grad).all()


def test_degenerate_single_sample_mmd_and_batch_contract():
 x=torch.zeros(1,4,requires_grad=True)
 value=mmd(x,x.detach());assert value.item()==0
 value.backward();assert torch.isfinite(x.grad).all()
 with pytest.raises(ValueError):mmd(torch.zeros(2,4),torch.zeros(1,4))


def test_exposure_identity_zero_pixels_and_constant_field():
 x=torch.rand(2,3,8,8);x[:,:,0]=0
 basis,coord=polynomial_basis(x,2)
 coef=torch.zeros(2,1,len(basis),requires_grad=True)
 flow=torch.zeros(2,2,2,2,requires_grad=True)
 out,_=exposure(x,coef,flow,basis,coord,20)
 assert torch.equal(out,x)
 out.sum().backward();assert torch.isfinite(coef.grad).all() and torch.isfinite(flow.grad).all()
 with torch.no_grad():coef[:,:,0]=.2
 out,_=exposure(x,coef,flow,basis,coord,20)
 assert torch.allclose(out,x*np.exp(.2),atol=1e-6)


def test_blur_matches_independent_reflection_convolution():
 x=torch.arange(7*7,dtype=torch.float64).reshape(1,1,7,7).repeat(1,3,1,1)/49
 precision=torch.full_like(x,1.2,requires_grad=True)
 out=adaptive_blur(x,precision,3)
 axis=np.arange(-1,2);kernel=np.exp(-.5*(axis[:,None]**2+axis[None,:]**2)*1.2**2);kernel/=kernel.sum()
 # torch reflection excludes the boundary sample: scipy mode='mirror'.
 expected=correlate(x[0,0].numpy(),kernel,mode='mirror')
 np.testing.assert_allclose(out[0,0].detach().numpy(),expected,rtol=1e-12,atol=1e-12)
 out.square().sum().backward();assert torch.isfinite(precision.grad).all()
 assert torch.allclose(adaptive_blur(torch.ones_like(x),precision.detach(),3),torch.ones_like(x))


@pytest.mark.parametrize('multi',[False,True])
def test_updates_budgets_frozen_features_and_mixture(multi):
 torch.manual_seed(11)
 model=torch.nn.Sequential(torch.nn.Flatten(),torch.nn.Linear(3*8*8,6)).eval().requires_grad_(False)
 before=copy.deepcopy(model.state_dict())
 clean=torch.rand(2,3,8,8)
 with torch.no_grad():reference=model(torch.rand_like(clean)).detach()
 cfg=AttackConfig(steps=2,degree=2,tune_scale=4,layers=3,total_epsilon=.07,noise_epsilon=.01)
 output,trace=attack(model,clean,reference,cfg,multilayer=multi)
 assert trace['updates']==2 and trace['trace'][-1]['update']==2
 assert torch.isfinite(output).all() and output.min()>=0 and output.max()<=1
 assert (output-clean).abs().max()<=.070001 and trace['max_noise']<=.010001
 for key,value in before.items():assert torch.equal(value,model.state_dict()[key])
 assert all(p.grad is None for p in model.parameters())
 if multi:
  weights=np.array(trace['mixture_weights']);np.testing.assert_allclose(weights.sum(-1),1,atol=1e-6)
  assert weights.shape==(3,2,4)
 control,details=attack(model,clean,reference,cfg,multilayer=multi,initialize_only=True)
 assert details['updates']==0 and len(details['trace'])==1
 assert torch.equal(control,attack(model,clean,reference,replace(cfg,steps=0),multilayer=multi)[0])


def test_reference_cycle_covers_full_fake_population_and_partial_tail():
 assigned=[]
 for offset in range(0,103,30):
  ids=reference_indices(offset,min(30,103-offset),60);assigned.extend(ids)
 assert len(assigned)==103 and assigned==[i%60 for i in range(103)]
 assert len(reference_indices(90,13,60))==13


def test_target_detach_and_invalid_settings():
 clean=torch.rand(1,3,8,8)
 with pytest.raises(ValueError,match='detached'):
  attack(lambda x:x.mean((2,3)),clean,torch.rand(1,3,requires_grad=True),AttackConfig(tune_scale=4))
 with pytest.raises(ValueError):AttackConfig(kernel=2).validate()


def test_mstat_uniform_initialization_is_parallel_three_layer_mixture():
 torch.manual_seed(9);x=.2+.5*torch.rand(2,3,32,32)
 feature=lambda z:z.mean((2,3))
 cfg=AttackConfig(steps=0,degree=2,tune_scale=4,total_epsilon=.2)
 actual,_=attack(feature,x,torch.full((2,3),.6),cfg,multilayer=True)
 expected=x
 precision=torch.full_like(x,100/np.sqrt(3*32*32))
 for _ in range(3):
  expected=.75*expected+.25*adaptive_blur(expected,precision,3)
  expected=torch.maximum(torch.minimum(expected,x+.2),x-.2).clamp(0,1)
 assert torch.allclose(actual,expected,atol=1e-7)
 assert (actual-x).abs().max()>.001


def test_one_noise_step_matches_explicit_mmd_descent():
 torch.manual_seed(13);x=.2+.5*torch.rand(2,3,8,8)
 feature=lambda z:z.flatten(1)[:,:12]
 ref=torch.full((2,12),.7)
 cfg=AttackConfig(steps=1,degree=2,tune_scale=4,total_epsilon=.2,noise_epsilon=.02,
                  exposure_lr=0,flow_lr=0,blur_lr=0,noise_lr=.01,lambda_bias=0,lambda_flow=0)
 initial,_=attack(feature,x,ref,replace(cfg,steps=0))
 noise=torch.zeros_like(x,requires_grad=True)
 loss=10*mmd(feature(initial+noise),ref)
 gradient=torch.autograd.grad(loss,noise)[0]
 expected=(initial-.01*gradient.sign()).clamp(0,1)
 actual,_=attack(feature,x,ref,cfg)
 assert torch.allclose(actual,expected,atol=1e-7)


def test_batch_checkpoint_rolls_back_partial_batch_and_resumes(tmp_path):
 from run_exp05 import connect
 db=connect(tmp_path/'state.sqlite')
 with db:
  db.execute('INSERT INTO frames VALUES(?,?,?)',('method',0,'first'))
  db.execute('INSERT INTO batches VALUES(?,?,?)',('method',0,'batch0'))
 with pytest.raises(RuntimeError):
  with db:
   db.execute('INSERT INTO frames VALUES(?,?,?)',('method',1,'partial'))
   raise RuntimeError('simulated power interruption before batch commit')
 db.close();db=connect(tmp_path/'state.sqlite')
 assert db.execute('SELECT idx,data FROM frames').fetchall()==[(0,'first')]
 assert db.execute('SELECT batch FROM batches').fetchall()==[(0,)]
 with db:
  db.execute('INSERT INTO frames VALUES(?,?,?)',('method',1,'resumed'))
  db.execute('INSERT INTO batches VALUES(?,?,?)',('method',1,'batch1'))
 assert db.execute('SELECT COUNT(*) FROM frames').fetchone()[0]==2
 db.close()


def test_unchanged_rows_reset_adversarial_evidence():
 from run_exp05 import unchanged
 source={'label':0,'clean_score':.2,'attacked_score':.8,'linf':.1}
 for field in ('mean','abs_mean','variance','energy','gates'):
  source[field+'_clean']=[1.,2.];source[field+'_attacked']=[9.,9.]
 out=unchanged(source)
 assert out['attacked_score']==.2 and out['linf']==0 and out['ssim']==1 and not out['attack_applied']
 assert out['energy_clean']==out['energy_attacked'] and source['energy_attacked']==[9.,9.]
