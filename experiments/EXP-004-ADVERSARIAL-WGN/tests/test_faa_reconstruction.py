import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.fft import dctn
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'code'))
from attacks import block_transform
from jia_faa import FAAConfig, feasible_image, fusion_matrix, frequency_norm, reconstruct_faa, frequency_initialization_control
from paper_aligned_attacks import pgd_jia_reference, fgsm_jia_reference

torch.set_num_threads(2)


class Detector(torch.nn.Module):
    def forward(self, x):
        return 4-8*x.mean((1, 2, 3))


def test_dct_matches_independent_scipy():
    x = torch.rand(2,3,16,24,dtype=torch.float64)
    blocks = x.numpy().reshape(2,3,2,8,3,8).transpose(0,1,2,4,3,5)
    reference = dctn(blocks,type=2,axes=(-2,-1),norm='ortho').transpose(0,1,2,4,3,5).reshape(x.shape)
    np.testing.assert_allclose(block_transform(x).numpy(),reference,atol=1e-13)


def test_dct_gradient_matches_finite_difference():
    x = torch.rand(1,1,4,4,dtype=torch.float64,requires_grad=True)
    assert torch.autograd.gradcheck(lambda value: block_transform(value,2), (x,))


@pytest.mark.parametrize('norm', ['linf','l2'])
def test_final_rgb_and_frequency_constraints_after_clipping(norm):
    torch.manual_seed(5)
    original = torch.rand(3,3,16,16)
    original[0,0,0,0] = 0
    original[1,0,0,0] = 1
    result = feasible_image(torch.randn_like(original)*10,original,.03,8,norm)
    assert result.min()>=0 and result.max()<=1
    assert (frequency_norm(result-original,8,norm)<=.03+1e-6).all()
    assert (result-original).abs().sum()>0


def test_energy_matrix_handles_black_input():
    matrix = fusion_matrix(torch.zeros(2,3,16,16),8,'energy-proportion')
    assert torch.isfinite(matrix).all()
    assert torch.allclose(matrix,torch.full_like(matrix,1/64))


def test_faa_one_update_matches_declared_recurrence():
    original = torch.full((1,3,16,16),.2)
    model = Detector().eval()
    cfg = FAAConfig(.3,.1,1,'linf','uniform')
    torch.manual_seed(77)
    p = torch.rand_like(original).requires_grad_(True)
    coeff = block_transform(original)
    candidate = feasible_image(coeff+p,original,cfg.epsilon,8,'linf')
    loss = torch.nn.functional.softplus(-model(candidate)).sum()
    grad = torch.autograd.grad(loss,p)[0]
    expected = feasible_image(coeff+p.detach()+cfg.step_size*grad.sign(),original,cfg.epsilon,8,'linf')
    if model(expected)>=model(original):
        expected=original
    torch.manual_seed(77)
    actual = reconstruct_faa(model,original,cfg)
    assert torch.allclose(actual,expected,atol=2e-6)


@pytest.mark.parametrize('norm', ['linf','l2'])
def test_faa_retains_false_negative_and_valid_best_iterate(norm):
    x = torch.stack([torch.full((3,16,16),.2),torch.full((3,16,16),.8)])
    model = Detector().eval()
    cfg = FAAConfig(.1,.05,5,norm,'energy-proportion')
    result = reconstruct_faa(model,x,cfg)
    assert torch.equal(result[1],x[1])
    assert (frequency_norm(result-x,8,norm)<=.1+1e-6).all()
    assert (model(result)<=model(x)+1e-6).all()


def test_successful_faa_images_stop_independently():
    cfg = FAAConfig(8,.1,1,'linf','uniform')
    x = torch.full((1,3,16,16),.49)
    torch.manual_seed(4)
    first = reconstruct_faa(Detector(),x,cfg)
    assert Detector()(first)<0
    torch.manual_seed(4)
    longer = reconstruct_faa(Detector(),x,FAAConfig(8,.1,10,'linf','uniform'))
    assert torch.equal(first,longer)


def test_pgd_more_steps_retain_best_and_restarts_keep_clean_trajectory():
    x = torch.full((2,3,16,16),.2)
    model = Detector()
    one = pgd_jia_reference(model,x,.1,1,.03)
    many = pgd_jia_reference(model,x,.1,8,.03,restarts=3)
    assert (model(many)<=model(one)+1e-6).all()
    assert (many-x).abs().max()<=.1+1e-6


def test_nan_logits_are_rejected():
    class Broken(torch.nn.Module):
        def forward(self,x):return x.mean((1,2,3))*float('nan')
    with pytest.raises(FloatingPointError):
        reconstruct_faa(Broken(),torch.rand(1,3,16,16),FAAConfig(.1,.01,2,'linf','uniform'))


def test_confident_fake_bce_gradient_does_not_cancel_to_zero():
    class Confident(torch.nn.Module):
        def forward(self,x):return 50*x.mean((1,2,3))
    x=torch.full((1,3,16,16),.8)
    out=fgsm_jia_reference(Confident(),x,.01)
    assert torch.allclose(out,x-.01,atol=1e-6)
    assert Confident()(out)<Confident()(x)


def test_faa_changes_no_parameters_or_buffers():
    class Buffered(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.bn=torch.nn.BatchNorm2d(3)
            self.scale=torch.nn.Parameter(torch.ones(()))
        def forward(self,x):return 10+self.scale*self.bn(x).mean((1,2,3))
    model=Buffered().eval().requires_grad_(False)
    before={k:v.clone() for k,v in model.state_dict().items()}
    reconstruct_faa(model,torch.rand(2,3,16,16),FAAConfig(.1,.01,3,'linf','uniform'))
    for key,value in before.items():assert torch.equal(value,model.state_dict()[key])


def test_frequency_initialization_control_uses_same_seed_and_no_optimization():
    x=torch.full((2,3,16,16),.2)
    cfg=FAAConfig(.1,.01,3,'linf','uniform')
    torch.manual_seed(9)
    perturbation=torch.rand_like(x)
    expected=feasible_image(block_transform(x)+perturbation,x,.1,8,'linf')
    torch.manual_seed(9)
    actual=frequency_initialization_control(Detector(),x,cfg)
    assert torch.equal(actual,expected)
