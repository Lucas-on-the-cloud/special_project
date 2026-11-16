import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
import torch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'code'))
from evaluation_data import load_records, cohort_fingerprint, ffpp_pair_mapping, source_cluster
from image_quality import image_quality
from restore_lab_data import safe_relative
from run_exp04_v2 import select_pilot, evaluation_summary
from run_exp04_v3 import validate_settings

REPO = Path(__file__).resolve().parents[3]


def test_sampler_unique_when_multiple_frames_per_video_needed():
    records=[SimpleNamespace(label=y,manipulation=g,video=str(v))
             for y,g in [(0,'Real'),(1,'DF'),(1,'FS')]
             for v in range(3) for frame in range(10)]
    chosen=select_pilot(records,40,1024)
    assert len(chosen)==len(set(chosen))==40
    assert chosen==select_pilot(records,40,1024)


def test_dfdc_adapter_and_portable_identity(tmp_path):
    manifest=tmp_path/'DFDC.json'
    manifest.write_text(json.dumps({'DFDC':{'DFDC_Real':{'test':{'r':{'frames':['DFDC\\r\\0.png']}}},
                                            'DFDC_Fake':{'test':{'f':{'frames':['DFDC\\f\\0.png']}}}}}))
    records=load_records(REPO,manifest,tmp_path,{},'dfdc')
    assert [r.label for r in records]==[0,1]
    assert len(cohort_fingerprint(records,tmp_path))==64
    other=tmp_path/'other'
    manifest2=manifest
    moved=load_records(REPO,manifest2,other,{},'dfdc')
    assert cohort_fingerprint(records,tmp_path)==cohort_fingerprint(moved,other)


def test_duplicate_dfdc_paths_are_rejected(tmp_path):
    manifest=tmp_path/'DFDC.json'
    manifest.write_text(json.dumps({'DFDC':{g:{'test':{'v':{'frames':['same.png']}}}
                                            for g in ['DFDC_Real','DFDC_Fake']}}))
    with pytest.raises(ValueError,match='Duplicate'):
        load_records(REPO,manifest,tmp_path,{},'dfdc')


@pytest.mark.parametrize('dataset,name,real,fake', [
    ('celebdf','Celeb-DF-v2-official-direct','CelebDFv2Official_real','CelebDFv2Official_fake'),
    ('wilddeepfake','WildDeepfake','WildDeepfake_Real','WildDeepfake_Fake'),
])
def test_external_adapter_uses_all_test_frames_only(tmp_path,dataset,name,real,fake):
    manifest=tmp_path/'manifest.json'
    manifest.write_text(json.dumps({name:{group:{
        'train':{'train':{'frames':['do-not-use.png']}},
        'test':{video:{'frames':[f'{video}/0.png',f'{video}/1.png']}}}
        for group,video in [(real,'r'),(fake,'f')]}}))
    records=load_records(REPO,manifest,tmp_path,{},dataset)
    assert [(r.label,r.video,r.manipulation) for r in records]==[(0,'r',real)]*2+[(1,'f',fake)]*2
    assert all(r.path.name!='do-not-use.png' for r in records)
    assert source_cluster('f',dataset,{})==dataset+'-video:f'
    moved=load_records(REPO,manifest,tmp_path/'moved',{},dataset)
    assert cohort_fingerprint(records,tmp_path)==cohort_fingerprint(moved,tmp_path/'moved')


@pytest.mark.parametrize('path',['../escape','/absolute','C:\\outside','safe/../../outside'])
def test_restore_rejects_unsafe_paths(path):
    with pytest.raises(ValueError):safe_relative(path)


def test_quality_identity_and_known_constant_mse():
    x=torch.full((1,3,16,16),.5)
    identity=image_quality(x,x)[0]
    assert identity['mse']==0 and identity['psnr_db'] is None
    assert identity['ssim']==pytest.approx(1,abs=2e-5)
    shifted=image_quality(x,x+.1)[0]
    assert shifted['mse']==pytest.approx(.01,abs=1e-6)
    assert shifted['psnr_db']==pytest.approx(20,abs=1e-4)
    expected=(2*.5*.6+.01**2)/(.5**2+.6**2+.01**2)
    assert shifted['ssim']==pytest.approx(expected,abs=2e-4)


def test_empty_eligibility_is_null_and_nan_is_rejected():
    rows=[dict(label=y,clean_score=.2,attacked_score=.1 if y else .2,linf=0.,attention_mae=0.,gates_mae=0.) for y in [0,1]]
    assert evaluation_summary(rows,'pgd')['asr_fake_given_clean_correct'] is None
    rows[0]['attacked_score']=float('nan')
    with pytest.raises(FloatingPointError):evaluation_summary(rows,'pgd')


def test_development_test_attacks_are_rejected():
    args=SimpleNamespace(epsilon=.1,alpha=.01,steps=3,pgd_restarts=2,batch_size=4,workers=0,
        max_samples=40,block=8,methods=['fgsm'],dataset='ffpp',compression='c23',purpose='development',split='test')
    with pytest.raises(ValueError,match='validation'):
        validate_settings(args)


def test_ffpp_real_and_both_fake_directions_share_source_cluster():
    mapping=ffpp_pair_mapping(REPO,'test')
    pairs=json.loads((REPO/'experiments/EXP-002-WGN/reproduction/code/splits/test.json').read_text())
    first,second=pairs[0]
    assert source_cluster(first,'ffpp',mapping)==source_cluster(second,'ffpp',mapping)
    assert source_cluster(first+'_'+second,'ffpp',mapping)==source_cluster(second+'_'+first,'ffpp',mapping)
