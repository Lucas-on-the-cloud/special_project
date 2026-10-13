from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F

import timm


class WaveletGuidedSpatialAttention(nn.Module):
    """WGSA reconstructed from Eqs. (2)--(10) of the WGN paper."""

    def __init__(self, gate_hidden_dim: int = 4, eps: float = 1e-6) -> None:
        super().__init__()
        self.eps = eps
        self.gate = nn.Sequential(
            nn.Linear(4, gate_hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(gate_hidden_dim, 4),
            nn.Sigmoid(),
        )

        # Outer products of h=[1,1]/sqrt(2) and g=[1,-1]/sqrt(2).
        kernels = torch.tensor(
            [
                [[1.0, 1.0], [1.0, 1.0]],
                [[1.0, -1.0], [1.0, -1.0]],
                [[1.0, 1.0], [-1.0, -1.0]],
                [[1.0, -1.0], [-1.0, 1.0]],
            ],
            dtype=torch.float32,
        ).unsqueeze(1) / 2.0
        self.register_buffer("haar_kernels", kernels, persistent=True)

    def forward(self, features: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        mean_map = features.mean(dim=1, keepdim=True)
        max_map = features.amax(dim=1, keepdim=True)
        guide = 0.5 * (mean_map + max_map)

        subbands = F.conv2d(guide, self.haar_kernels, stride=2)
        statistics = subbands.mean(dim=(2, 3))
        gates = self.gate(statistics).unsqueeze(-1).unsqueeze(-1)
        weighted = subbands * gates
        raw_attention = F.conv_transpose2d(weighted, self.haar_kernels, stride=2)

        spatial_min = raw_attention.amin(dim=(2, 3), keepdim=True)
        spatial_max = raw_attention.amax(dim=(2, 3), keepdim=True)
        attention = (raw_attention - spatial_min) / (spatial_max - spatial_min + self.eps)
        return features * attention, attention


class WaveletGuidedNetwork(nn.Module):
    """MobileViT-S + WGSA + concatenation fusion from the WGN paper."""

    def __init__(
        self,
        pretrained: bool = True,
        backbone_name: str = "mobilevit_s.cvnets_in1k",
        gate_hidden_dim: int = 4,
    ) -> None:
        super().__init__()
        self.backbone = timm.create_model(
            backbone_name,
            pretrained=pretrained,
            num_classes=0,
            global_pool="",
        )
        channels = self.backbone.num_features
        self.wgsa = WaveletGuidedSpatialAttention(gate_hidden_dim=gate_hidden_dim)
        self.fusion = nn.Sequential(
            nn.Conv2d(channels * 2, channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.ReLU(inplace=True),
        )
        self.classifier = nn.Linear(channels, 1)

    def forward_features(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        features = self.backbone.forward_features(images)
        attended, attention = self.wgsa(features)
        fused = self.fusion(torch.cat((features, attended), dim=1))
        return fused, attention

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        fused, _ = self.forward_features(images)
        pooled = fused.mean(dim=(2, 3))
        return self.classifier(pooled).squeeze(1)

