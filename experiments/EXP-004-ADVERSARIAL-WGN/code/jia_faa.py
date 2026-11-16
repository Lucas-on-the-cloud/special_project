"""Explicit reconstruction of Jia CVPR 2022 Algorithm 1, not author code.

Preserves block DCT, P~U(0,1), weighted fusion and sign-gradient P updates.
M construction and final constraint handling are declared operational choices.
No default frequency budget or M policy is inferred from the paper.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import torch
from torch.nn import functional as F

from attacks import block_transform


def require_finite(value, name):
    if not torch.isfinite(value).all():
        raise FloatingPointError(f'Non-finite {name}')
    return value


def checked_logits(model, images):
    logits = require_finite(model(images).reshape(-1), 'detector logits')
    if logits.shape != (len(images),):
        raise ValueError('Expected one logit per image')
    return logits


def validate_images(images):
    if images.ndim != 4 or not len(images) or not images.is_floating_point():
        raise ValueError('Expected a nonempty floating BCHW tensor')
    require_finite(images, 'input')
    if images.min() < 0 or images.max() > 1:
        raise ValueError('Expected RGB values in [0,1]')


def frequency_norm(delta, block, norm):
    coeff = block_transform(delta, block).flatten(1)
    if norm == 'linf':
        return coeff.abs().amax(1)
    if norm == 'l2':
        return torch.linalg.vector_norm(coeff, dim=1)
    raise ValueError('Frequency norm must be linf or l2')


def feasible_image(coefficients, original, epsilon, block, norm):
    """RGB clamp followed by radial DCT-norm contraction toward original.

    This is a declared feasibility map, not an author-verified projection.
    Both bounds apply to the final RGB tensor. Scaling a valid RGB difference
    toward its valid original preserves the RGB box by convexity.
    """
    candidate = block_transform(coefficients, block, inverse=True).clamp(0, 1)
    delta = candidate - original
    measured = frequency_norm(delta, block, norm)
    scale = (epsilon / measured.clamp_min(torch.finfo(delta.dtype).eps)).clamp(max=1)
    return original + scale[:, None, None, None] * delta


def fusion_matrix(original, block, policy):
    """Explicit policies; none is asserted to equal the authors' exact M."""
    b, c, h, w = original.shape
    coeff = block_transform(original.detach(), block)
    bands = coeff.reshape(b, c, h//block, block, w//block, block).permute(0, 1, 2, 4, 3, 5)
    if policy == 'energy-proportion':
        statistic = bands.square().mean((2, 3))
        total = statistic.sum((-2, -1), keepdim=True)
        weight = torch.where(total > 0, statistic / total.clamp_min(1e-12),
                             torch.full_like(statistic, 1/(block*block)))
    elif policy == 'legacy-magnitude-max':
        statistic = bands.abs().mean((2, 3))
        weight = .1 + .9 * statistic / (statistic.amax((-2, -1), keepdim=True) + 1e-8)
    elif policy == 'uniform':
        weight = torch.ones((b, c, block, block), device=original.device, dtype=original.dtype)
    else:
        raise ValueError('Declare energy-proportion, legacy-magnitude-max, or uniform M')
    return weight[:, :, None, None].expand(-1, -1, h//block, w//block, -1, -1).permute(0, 1, 2, 4, 3, 5).reshape_as(original).detach()


@dataclass(frozen=True)
class FAAConfig:
    epsilon: float
    step_size: float
    steps: int
    norm: str
    matrix_policy: str
    block: int = 8
    initialization_scale: float = 1.0
    stop_on_success: bool = True

    def validate(self):
        if not all(math.isfinite(x) and x > 0 for x in (self.epsilon, self.step_size)):
            raise ValueError('Explicit positive finite frequency epsilon/step size required')
        if self.steps < 1 or self.block < 2 or self.norm not in ('linf', 'l2'):
            raise ValueError('Invalid steps, block or norm')
        if not math.isfinite(self.initialization_scale) or self.initialization_scale < 0:
            raise ValueError('Invalid initialization scale')
        if self.matrix_policy not in ('energy-proportion', 'legacy-magnitude-max', 'uniform'):
            raise ValueError('Explicit M policy required')


def frequency_initialization_control(model, images, config):
    """Same M/U(0,1)/feasibility as FAA, with no gradient update.

    Paired seeds in the evaluator distinguish optimization from random
    frequency corruption. This is a project control, not a Jia method.
    """
    config.validate()
    validate_images(images)
    original=images.detach()
    matrix=fusion_matrix(original,config.block,config.matrix_policy)
    perturbation=torch.rand_like(original)*config.initialization_scale
    return feasible_image(block_transform(original,config.block)+matrix*perturbation,
                          original,config.epsilon,config.block,config.norm).detach()


def reconstruct_faa(model, images, config):
    """Return best feasible images; stop each eligible fake at first evasion.

    Call only for fake-labeled inputs. False negatives at the clean baseline
    are retained unchanged and never counted as new adversarial success.
    Exactly config.steps updates are used, an explicit loop-index convention.
    """
    config.validate()
    validate_images(images)
    if images.shape[-2] % config.block or images.shape[-1] % config.block:
        raise ValueError('DCT block must divide image dimensions')
    original = images.detach()
    matrix = fusion_matrix(original, config.block, config.matrix_policy)
    perturbation = torch.rand_like(original) * config.initialization_scale
    adv = original.clone()
    with torch.no_grad():
        initial_logits = checked_logits(model, original)
        best_loss = F.softplus(-initial_logits)
    best = original.clone()
    active = initial_logits >= 0
    for _ in range(config.steps):
        if not active.any():
            break
        variable = perturbation.detach().requires_grad_(True)
        coefficients = block_transform(adv.detach(), config.block)
        candidate = feasible_image(coefficients + matrix*variable, original,
                                   config.epsilon, config.block, config.norm)
        losses = F.softplus(-checked_logits(model, candidate))
        gradient = require_finite(torch.autograd.grad(losses[active].sum(), variable)[0], 'FAA gradient')
        perturbation = variable.detach() + config.step_size * gradient.sign()
        updated = feasible_image(coefficients + matrix*perturbation, original,
                                 config.epsilon, config.block, config.norm).detach()
        adv = torch.where(active[:, None, None, None], updated, adv)
        with torch.no_grad():
            logits = checked_logits(model, adv)
            loss = F.softplus(-logits)
            improved = active & (loss > best_loss)
            best = torch.where(improved[:, None, None, None], adv, best)
            best_loss = torch.maximum(best_loss, loss)
            if config.stop_on_success:
                active = active & (logits >= 0)
    require_finite(best, 'FAA output')
    measured = frequency_norm(best-original, config.block, config.norm)
    if (measured > config.epsilon + max(1e-6, config.epsilon*1e-5)).any():
        raise AssertionError('Final-output frequency budget violation')
    return best.detach()
