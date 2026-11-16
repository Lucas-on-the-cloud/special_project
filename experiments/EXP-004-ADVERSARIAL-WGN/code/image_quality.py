"""RGB MSE/PSNR and original Gaussian-window SSIM, data range=1."""
import math
import torch
from torch.nn import functional as F


@torch.no_grad()
def image_quality(clean, attacked):
    if clean.shape != attacked.shape or min(clean.shape[-2:]) < 11:
        raise ValueError('Matching BCHW images at least 11x11 are required')
    mse = (clean-attacked).square().flatten(1).mean(1)
    axis = torch.arange(11, device=clean.device, dtype=clean.dtype)-5
    gaussian = torch.exp(-axis.square()/(2*1.5**2))
    gaussian = gaussian/gaussian.sum()
    kernel = (gaussian[:, None]*gaussian[None, :])[None, None].expand(clean.shape[1], 1, -1, -1)
    def average(x):
        return F.conv2d(x, kernel, groups=clean.shape[1])
    mean_x, mean_y = average(clean), average(attacked)
    var_x = (average(clean.square())-mean_x.square()).clamp_min(0)
    var_y = (average(attacked.square())-mean_y.square()).clamp_min(0)
    covariance = average(clean*attacked)-mean_x*mean_y
    ssim = (((2*mean_x*mean_y+.01**2)*(2*covariance+.03**2))/
            ((mean_x.square()+mean_y.square()+.01**2)*(var_x+var_y+.03**2))).flatten(1).mean(1)
    rows = []
    for error, similarity in zip(mse.cpu().tolist(), ssim.cpu().tolist()):
        rows.append({'mse':error, 'psnr_db':-10*math.log10(error) if error else None,
                     'ssim':similarity})
    return rows
