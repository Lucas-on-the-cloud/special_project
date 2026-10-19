from __future__ import annotations

import common  # adds the frozen reproduction source directory
import torch
from torch import nn
from torch.nn import functional as F
from wgn.model import WaveletGuidedNetwork


class GradientWGN(WaveletGuidedNetwork):
    """Fixed depthwise Sobel magnitude + a learned, three-way gated fusion."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        channels = self.backbone.num_features
        sobel_x = torch.tensor([[-1., 0., 1.], [-2., 0., 2.], [-1., 0., 1.]]) / 8
        self.register_buffer('sobel_x', sobel_x[None, None].repeat(channels, 1, 1, 1))
        self.register_buffer('sobel_y', sobel_x.T[None, None].repeat(channels, 1, 1, 1))
        self.gradient_projection = nn.Sequential(nn.Conv2d(channels, channels, 1, bias=False),
                                                 nn.BatchNorm2d(channels), nn.ReLU(inplace=True))
        self.branch_gate = nn.Linear(channels * 3, 3)
        nn.init.zeros_(self.branch_gate.weight)
        nn.init.zeros_(self.branch_gate.bias)
        self.fusion = nn.Sequential(nn.Conv2d(channels * 3, channels, 1, bias=False),
                                    nn.BatchNorm2d(channels), nn.ReLU(inplace=True))

    def forward_features(self, images):
        spatial = self.backbone.forward_features(images)
        guided, attention = self.wgsa(spatial)
        channels = spatial.shape[1]
        padded = F.pad(spatial, (1, 1, 1, 1), mode='replicate')
        gx = F.conv2d(padded, self.sobel_x, groups=channels)
        gy = F.conv2d(padded, self.sobel_y, groups=channels)
        gradient = self.gradient_projection(torch.sqrt(gx.square() + gy.square() + 1e-6))
        branches = (spatial, guided, gradient)
        pooled = torch.cat([x.mean((2, 3)) for x in branches], dim=1)
        gates = self.branch_gate(pooled).softmax(dim=1) * 3.0
        merged = torch.cat([branch * gates[:, i, None, None, None]
                            for i, branch in enumerate(branches)], dim=1)
        return self.fusion(merged), attention
