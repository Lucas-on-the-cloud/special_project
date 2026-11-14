import sys
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"code"))
from run_exp04_v2 import select_pilot,evaluation_summary

def fake_records():
    records=[]
    for label,group in ((0,"FF-real"),(1,"FF-DF"),(1,"FF-F2F"),(1,"FF-FS"),(1,"FF-NT")):
        for vid in range(10):
            for frame in range(3):
                records.append(SimpleNamespace(label=label,manipulation=group,video=f"v{vid:03d}",
                                               path=f"{group}_{vid}_{frame}.png"))
    return records

def test_pilot_has_both_classes_and_multiple_manipulations():
    records=fake_records()
    selected=select_pilot(records,40,1024)
    assert selected==select_pilot(records,40,1024)
    assert len(selected)==40
    assert {records[i].label for i in selected}=={0,1}
    assert len({records[i].manipulation for i in selected if records[i].label==1})==4
    assert len({records[i].video for i in selected})>=8

def test_fooling_is_conditioned_on_clean_correct_fake_only():
    rows=[
     {"label":0,"clean_score":.15,"attacked_score":.15,"linf":0.,
      "attention_mae":0.,"gates_mae":0.},
     {"label":1,"clean_score":.9,"attacked_score":.1,"linf":4/255,
      "attention_mae":.2,"gates_mae":.03},
     {"label":1,"clean_score":.2,"attacked_score":.1,"linf":2/255,
      "attention_mae":.1,"gates_mae":.01},
    ]
    result=evaluation_summary(rows,"fgsm")
    assert result["eligible_clean_correct_fake"]==1
    assert result["fake_to_real_flips"]==1
    assert result["asr_fake_given_clean_correct"]==1.
    assert result["unconditional_fake_evasion"]==1.
    assert result["attacked_fake_clean_real_frame_auc"] is not None
