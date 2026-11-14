import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
import torch
from paper_aligned_attacks import attack

class Toy(torch.nn.Module):
    def __init__(self):
        super().__init__();self.fc=torch.nn.Linear(3,1,bias=False)
    def forward(self,x):
        pooled=x.mean((2,3))
        return self.fc(pooled).squeeze(1)

def test_attack_does_not_change_model_parameters():
    torch.manual_seed(8)
    model=Toy().eval()
    before={k:v.detach().clone() for k,v in model.state_dict().items()}
    x=torch.rand(2,3,16,16)
    for name in ("fgsm","pgd","jia-faa-adapt"):
        _=attack(model,x,name,epsilon=4/255,steps=2,alpha=1/255,block=8)
    after=model.state_dict()
    for key in before:
        assert torch.equal(before[key],after[key]),key
