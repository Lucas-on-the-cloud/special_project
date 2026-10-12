# Professor Update Email

**Subject: DFD-HR Reproduction – Training Time and Open Questions**

Dear Professor,

I would like to report the current status of the DFD-HR reproduction. We tested the official code on three environments: an RTX 4080 16 GB, a Linux Docker environment with an NVIDIA V100, and an RTX 5090 32 GB.

The RTX 5090 runs the model successfully, but the official batch size of 16 does not fit safely. I therefore used a physical batch size of 4 with four-step gradient accumulation, preserving an effective batch size of 16.

The run reached 1,079/7,192 iterations after 1 hour 25 minutes, corresponding to approximately 9–10 hours per epoch. The repository specifies 20 epochs, while its loop appears to execute epochs 0–20, potentially requiring 21 epochs. A complete single-GPU run would therefore take approximately 8–9 days.

Several details remain unclear: the authors' GPU model/count, training precision, exact epoch count, and whether batch size 16 is global or per GPU. The paper also specifies 32 inference frames, whereas the repository uses 8.

I have paused training to avoid unnecessary compute costs. I propose either using four GPUs, as suggested by the official launcher, or benchmarking a faithful optimized version using BF16 and improved data loading.

Could you please advise which direction would be preferable?

Best regards,  
[Your Name]
