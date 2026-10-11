# Experiments

No deepfake experiment has been run yet. `EXP-001` is the planned fresh-training reproduction of DFD-HR on the rented EZYCLOUDX V100 container. It uses the official DFD-HR code at a pinned commit and the paper's FaceForensics++ c23 protocol, subject to approved dataset access and verified splits. The authors' released DFD-HR final checkpoint will not be used for training; the official pretrained CLIP backbone remains part of the method initialization.

See [`EXP-001-DFD-HR/README.md`](EXP-001-DFD-HR/README.md) for the staged runbook and result table. Each experiment folder must document its hypothesis, data split, configuration, metrics, artifacts, result, and decision.
