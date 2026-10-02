# Kaggle Notebooks

The project uses Kaggle for all training and evaluation.

No deepfake notebook has been completed yet. The planned first notebook is a small DFD-HR checkpoint evaluation; it will be created after the Week 4 dataset and dependency gates pass. A maintained DeepfakeBench baseline is the fallback if DFD-HR cannot run reliably on Kaggle.

Notebook requirements:

- run top to bottom on Kaggle;
- record Python, PyTorch, CUDA, GPU, seed, source commit, and dataset version;
- separate smoke runs from full experiments;
- export compact JSON/CSV summaries;
- never embed credentials or commit datasets/checkpoints.
