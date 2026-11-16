"""Deterministic, dependency-free tables from audited EXP-004 compact evidence.

Run from any directory with Python3. --check verifies committed exports without
rewriting them. All CSV floats retain Python/JSON round-trip precision; only
the Markdown presentation rounds values. No runtime media or face paths read.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'
METHODS=('fgsm','pgd','frequency-init-control','jia-faa-reconstruction')
DATASETS=(('ffpp','FF++ c23','initial-evaluation.json'),
          ('dfdc','DFDC','full-dfdc-evaluation.json'),
          ('celebdf','Celeb-DF-v2 official-direct','full-celebdf-evaluation.json'),
          ('wilddeepfake','WildDeepfake','full-wilddeepfake-evaluation.json'))


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_text(rows):
    names=list(dict.fromkeys(key for row in rows for key in row))
    output=io.StringIO(newline='')
    writer=csv.DictWriter(output,fieldnames=names,lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return output.getvalue()


def fmt(value,digits=6,percent=False):
    if value is None:return '—'
    return f'{value*100:.2f}%' if percent else f'{value:.{digits}f}'


def table(header,rows):
    return '\n'.join(['| '+' | '.join(header)+' |','|'+'|'.join('---' for _ in header)+'|',
                      *['| '+' | '.join(map(str,row))+' |' for row in rows]])


def numeric_leaves(value,pointer=''):
    if isinstance(value,dict):
        for key,child in value.items():
            escaped=key.replace('~','~0').replace('/','~1')
            yield from numeric_leaves(child,pointer+'/'+escaped)
    elif isinstance(value,list):
        for i,child in enumerate(value):yield from numeric_leaves(child,pointer+'/'+str(i))
    elif value is None or isinstance(value,(bool,int,float)):
        yield pointer,value


def generate(destination):
    destination.mkdir(parents=True,exist_ok=True)
    cohorts=[];methods=[];videos=[];manipulations=[];outcomes=[];bands=[];paired=[];numeric=[]
    inputs={};attack_settings=None
    for key,label,filename in DATASETS:
        path=RESULTS/filename;inputs[filename]=sha(path)
        raw=json.loads(path.read_text())
        data=raw['datasets']['ffpp'] if key=='ffpp' else raw
        assert data['audits_passed']
        cohort=data['locked_cohort'];clean=data['clean_full_reference'];meta=data['metadata']
        assert clean['passed'] and cohort['frames']==cohort['real']+cohort['fake']==clean['frames']
        assert cohort['cohort_fingerprint']==meta['cohort_fingerprint']==clean['portable_cohort_fingerprint']
        settings={k:v for k,v in meta['settings'].items() if k!='dataset'}
        if attack_settings is None:attack_settings=settings
        else:assert settings==attack_settings
        eligible=data['methods']['fgsm']['summary']['eligible_clean_correct_fake']
        cohorts.append(dict(dataset=key,dataset_label=label,frames=cohort['frames'],real=cohort['real'],fake=cohort['fake'],
            eligible_fake=eligible,baseline_false_negative_fake=cohort['fake']-eligible,
            video_sequence_records=data['methods']['fgsm']['video_analysis']['video_count'],
            clean_frame_accuracy=clean['accuracy'],clean_frame_auc=clean['auc'],
            clean_reference_accuracy_abs_diff=clean['accuracy_abs_diff'],clean_reference_auc_abs_diff=clean['auc_abs_diff'],
            clean_reference_tolerance=clean['tolerance'],checkpoint_sha256=meta['checkpoint_sha256'],
            manifest_sha256=meta['manifest_sha256'],cohort_fingerprint=meta['cohort_fingerprint'],
            protocol_lock_sha256=meta['protocol_lock_sha256'],evidence_file=filename))
        for method in METHODS:
            item=data['methods'][method];s=item['summary'];v=item['video_analysis'];q=item['eligible_quality_and_diagnostics']
            assert s['total_frames']==cohort['frames'] and s['fake_frames']==cohort['fake']
            assert s['eligible_clean_correct_fake']==eligible==q['frames']
            assert v['frame_counts']['fake_to_real_flips']==s['fake_to_real_flips']
            assert abs(s['asr_fake_given_clean_correct']-s['fake_to_real_flips']/eligible)<1e-14
            assert abs(s['clean_frame_accuracy']-clean['accuracy'])<=clean['tolerance']
            assert abs(s['clean_frame_auc']-clean['auc'])<=clean['tolerance']
            low,high=v['frame_asr_95pct_cluster_bootstrap']
            row=dict(dataset=key,dataset_label=label,**s,frame_asr_ci95_low=low,frame_asr_ci95_high=high,
                bootstrap_clusters=v['bootstrap_clusters'],interval_exploratory=key!='ffpp',
                nonzero_eligible_frames=item['nonzero_eligible_frames'])
            for field,description in q.items():
                if field in ('frames','bands'):continue
                for statistic,value in description.items():row['eligible_'+field+'_'+statistic]=value
            assert q['psnr_db']['finite_count']<=eligible and q['ssim']['finite_count']==eligible
            methods.append(row)
            videos.append(dict(dataset=key,method=method,video_sequence_records=v['video_count'],
                eligible_fake_video_sequence=v['video_counts']['eligible_clean_correct_fake'],
                flipped_fake_video_sequence=v['video_counts']['fake_to_real_flips'],video_asr=v['video_fake_asr'],
                clean_video_auc=v['clean_video_auc'],attacked_fake_clean_real_video_auc=v['attacked_fake_clean_real_video_auc']))
            for group,values in v['by_manipulation'].items():
                manipulations.append(dict(dataset=key,method=method,manipulation=group,
                    **{k:values[k] for k in ('total_fake_frames','eligible_clean_correct_fake','fake_to_real_flips','asr_conditional')}))
            for outcome,values in v['mechanism_success_vs_failure'].items():
                outcomes.append(dict(dataset=key,method=method,outcome=outcome,**values))
            for descriptor,values in q['bands'].items():
                for index,(before,drift) in enumerate(zip(values['clean_mean'],values['absolute_drift_mean'])):
                    bands.append(dict(dataset=key,method=method,population='clean-correct Fake',descriptor=descriptor,
                        haar_kernel_index=index,clean_mean=before,absolute_drift_mean=drift))
        p=data['frequency_paired_comparison'];cells=p['paired_flip_table'];lo,hi=p['difference_95pct_cluster_bootstrap']
        assert sum(cells.values())==eligible
        paired.append(dict(dataset=key,eligible_fake=eligible,both=cells.get('FAA_1_control_1',0),
            faa_only=cells.get('FAA_1_control_0',0),control_only=cells.get('FAA_0_control_1',0),
            neither=cells.get('FAA_0_control_0',0),faa_minus_control_asr=p['asr_difference_faa_minus_control'],
            difference_ci95_low=lo,difference_ci95_high=hi))
        for pointer,value in numeric_leaves(data):
            numeric.append(dict(dataset=key,json_pointer=pointer,json_value=json.dumps(value,allow_nan=False)))
    assert len(cohorts)==4 and len(methods)==16 and len(videos)==16 and len(bands)==320
    assert sum(r['frames'] for r in cohorts)==325554 and sum(r['eligible_fake'] for r in cohorts)==145064
    exports={'cohorts.csv':cohorts,'methods.csv':methods,'videos.csv':videos,'manipulations.csv':manipulations,
             'mechanism-outcomes.csv':outcomes,'haar-bands.csv':bands,'paired-frequency.csv':paired,'all-numeric-values.csv':numeric}
    for filename,rows in exports.items():(destination/filename).write_text(csv_text(rows))
    lines=['# EXP-004 — Complete result tables','',
        'Bốn full processed test manifests; frozen WGN. Giá trị hiển thị được làm tròn; CSV giữ full precision từ evidence JSON. Không tính train/validation vào population báo cáo.','',
        '## 1. Cohort và clean reference','',
        table(['Dataset','Frames','Real','Fake','Video/sequence','Eligible Fake','Baseline Fake FN','Clean ACC','Clean AUC'],[
            [r['dataset_label'],r['frames'],r['real'],r['fake'],r['video_sequence_records'],r['eligible_fake'],r['baseline_false_negative_fake'],
             fmt(r['clean_frame_accuracy'],percent=True),fmt(r['clean_frame_auc'],percent=True)] for r in cohorts]),'',
        'ASR = Fake clean-correct mới chuyển thành Real / tất cả Fake clean-correct. Real và baseline Fake false negatives giữ nguyên. Video/sequence records không đồng nghĩa independent source videos.','',
        '## 2. Frame attack results — đủ 16 tổ hợp','',
        table(['Dataset','Method','Flips / eligible','ASR','95% cluster CI','Attacked ACC','Attacked AUC'],[
            [r['dataset'],r['method'],f"{r['fake_to_real_flips']}/{r['eligible_clean_correct_fake']}",fmt(r['asr_fake_given_clean_correct'],percent=True),
             fmt(r['frame_asr_ci95_low'],percent=True)+'–'+fmt(r['frame_asr_ci95_high'],percent=True),
             fmt(r['attacked_fake_clean_real_frame_accuracy'],percent=True),fmt(r['attacked_fake_clean_real_frame_auc'],percent=True)] for r in methods]),'',
        'ACC/AUC sau attack dùng attacked Fake + clean Real. Bootstrap 1.000 replicates; FF++ theo 70 official source pairs, external theo video/sequence IDs. External intervals exploratory do thiếu original-source/identity linkage.','',
        '## 3. Chất lượng ảnh và chi phí','',
        table(['Dataset','Method','Finite PSNR n','PSNR mean dB','SSIM mean','Pixel L∞ max','DCT L∞ max','Runtime s','Peak allocated MiB'],[
            [r['dataset'],r['method'],r['eligible_psnr_db_finite_count'],fmt(r['eligible_psnr_db_mean'],3),fmt(r['eligible_ssim_mean']),
             fmt(r['eligible_linf_maximum'],9),fmt(r['eligible_dct_linf_maximum'],9),fmt(r['seconds'],3),fmt(r['peak_allocated_mib'],1)] for r in methods]),'',
        'Quality/norm summaries condition on eligible Fake. PSNR của ảnh không đổi là vô hạn, không đi vào finite mean; SSIM finite count bằng eligible count. CSV còn có MSE, DCT L2, median, p05/p95, min/max và finite counts. Runtime gồm loader/attack/quality/diagnostics/ghi output; peak allocated khác tổng reserved/device memory. SSIM không chứng minh imperceptibility.','',
        '## 4. Video/sequence aggregation','',
        table(['Dataset','Method','Video/sequence records','Flips / eligible Fake groups','Group ASR','Clean AUC','Attacked AUC'],[
            [r['dataset'],r['method'],r['video_sequence_records'],f"{r['flipped_fake_video_sequence']}/{r['eligible_fake_video_sequence']}",
             fmt(r['video_asr'],percent=True),fmt(r['clean_video_auc'],percent=True),fmt(r['attacked_fake_clean_real_video_auc'],percent=True)] for r in videos]),'',
        'Group score là mean frame score trên cohort đã chọn, threshold 0.5; không đồng nhất frame eligibility và video/sequence eligibility.','',
        '## 5. Theo manipulation / Fake group','',
        table(['Dataset','Method','Fake group','Fake frames','Flips / eligible','ASR'],[
            [r['dataset'],r['method'],r['manipulation'],r['total_fake_frames'],f"{r['fake_to_real_flips']}/{r['eligible_clean_correct_fake']}",fmt(r['asr_conditional'],percent=True)] for r in manipulations]),'',
        '## 6. FAA và paired initialization control','',
        table(['Dataset','Both flip','FAA only','Control only','Neither','FAA−control pp','95% difference CI pp'],[
            [r['dataset'],r['both'],r['faa_only'],r['control_only'],r['neither'],fmt(100*r['faa_minus_control_asr'],2),
             fmt(100*r['difference_ci95_low'],2)+'–'+fmt(100*r['difference_ci95_high'],2)] for r in paired]),'',
        'Control-only outcomes được giữ nguyên: FAA không giữ riêng P0 initialization trước update đầu tiên. Không sửa thuật toán sau test để loại các case này.','',
        '## 7. FAA diagnostics theo thành công / thất bại','',
        table(['Dataset','Outcome','Frames','Gate MAE','Attention MAE','Variance MAE','Energy MAE'],[
            [r['dataset'],r['outcome'],r['frames'],fmt(r['gates_mae_mean'],9),fmt(r['attention_mae_mean'],9),
             fmt(r['variance_mae_mean'],9),fmt(r['energy_mae_mean'],9)] for r in outcomes if r['method']=='jia-faa-reconstruction']),'',
        'Đây là liên hệ mô tả, không quy nguyên nhân riêng cho WGSA. `mechanism-outcomes.csv` có đủ cả bốn methods; `haar-bands.csv` có 320 rows signed/absolute mean, variance, energy và gates theo từng kernel. Index kernel 0–3 theo thứ tự buffer của frozen WGN, không suy đoán quy ước đặt tên LH/HL.','',
        '## 8. Protocol và provenance','',
        'Frozen checkpoint SHA256 `'+cohorts[0]['checkpoint_sha256']+'`. Pixel FGSM/PGD L∞=4/255; PGD alpha=1/255,10 updates,5 trajectories. FAA: block8, energy-proportion M, global DCT L∞=0.1, P-step=0.01,10 updates, first-evasion stopping. Seed1024, batch32. Pixel/DCT budgets khác đơn vị; không coi đây là xếp hạng cùng ngân sách. FAA là reconstruction, chưa author-verified exact reproduction.','',
        'Các bảng chính dùng full DFDC132.116 frames; cohort DFDC2.000 ảnh ban đầu vẫn được giữ trong `initial-evaluation.json` để truy vết, không trộn vào full results.','',
        'Nguồn: [initial evidence (FF++ full)](../initial-evaluation.json), [DFDC full](../full-dfdc-evaluation.json), [Celeb-DF-v2 full](../full-celebdf-evaluation.json), [WildDeepfake full](../full-wilddeepfake-evaluation.json). [Tổng quan](../cross-dataset-overview.md).','',
        'CSV fractions nằm trong[0,1] cho ASR/ACC/AUC; các cột có `_pp` (nếu có) dùng điểm phần trăm. `all-numeric-values.csv` giữ mọi numeric/null/bool leaf theo RFC6901 JSON pointer, gồm các thống kê chưa đưa thành cột riêng. JSON `null` không bị biến thành0. Không công bố ảnh/weights/raw per-frame logs trong Git.','']
    (destination/'README.md').write_text('\n'.join(lines))
    manifest={'generator':'reporting/export_tables.py','generator_sha256':sha(Path(__file__)),
        'inputs_sha256':inputs,'rows':{name:len(rows) for name,rows in exports.items()},
        'outputs_sha256':{p.name:sha(p) for p in sorted(destination.iterdir()) if p.name!='PROVENANCE.json'},
        'scope':'four full processed test cohorts; clean-correct Fake evasion; source JSON precision retained'}
    (destination/'PROVENANCE.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    target=RESULTS/'tables'
    if args.check:
        with tempfile.TemporaryDirectory(prefix='exp04-tables-') as temporary:
            candidate=Path(temporary);generate(candidate)
            assert sorted(p.name for p in candidate.iterdir())==sorted(p.name for p in target.iterdir())
            for path in candidate.iterdir():assert path.read_bytes()==(target/path.name).read_bytes(),path.name
        print('EXP04_TABLES_VERIFIED')
    else:
        generate(target);print('EXP04_TABLES_EXPORTED '+str(target))


if __name__=='__main__':main()
