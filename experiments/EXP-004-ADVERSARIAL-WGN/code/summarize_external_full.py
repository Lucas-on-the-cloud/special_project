"""Audit each full external cohort and export compact evidence without media."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from summarize_final import METHODS, diagnostics, paired_frequency, read, sha

CORE = ('jia_faa.py', 'paper_aligned_attacks.py', 'diagnostics.py',
        'image_quality.py', 'run_exp04_v2.py')
LABELS = {'celebdf':'Celeb-DF-v2 official-direct', 'wilddeepfake':'WildDeepfake'}


def audit(runtime, dataset):
    folder = runtime/'runs'/f'final_{dataset}_full_reconstruction_001'
    final = read(folder/'results.json')
    cohort = read(runtime/'cohorts'/f'full_{dataset}.json')
    clean = read(runtime/'runs'/f'clean_{dataset}.json')
    prior = read(runtime/'runs/final_dfdc_full_reconstruction_001/results.json')['metadata']
    meta = final['metadata']
    assert final['complete'] and clean['passed']
    assert meta['settings']=={**prior['settings'],'dataset':dataset}
    assert meta['cohort_fingerprint']==meta['full_cohort_fingerprint']==cohort['cohort_fingerprint']==clean['portable_cohort_fingerprint']
    assert meta['checkpoint_sha256']==cohort['checkpoint_sha256']==clean['checkpoint_sha256']==prior['checkpoint_sha256']
    assert meta['manifest_sha256']==cohort['manifest_sha256']==clean['manifest_sha256']
    assert meta['protocol_lock_sha256']==cohort['protocol_lock_sha256']
    assert meta['selected_frames']==cohort['frames']==clean['frames']
    for name in CORE:
        assert meta['source_sha256'][name]==prior['source_sha256'][name], name
    for name, digest in meta['source_sha256'].items():
        assert sha(folder/'source'/name)==digest, name
    expected = {hashlib.sha256(r['path'].encode()).hexdigest()[:16]:r for r in cohort['records']}
    assert len(expected)==cohort['frames']
    output = {'scope':LABELS[dataset]+' full processed test manifest; frozen WGN; FAA reconstruction',
        'metadata':meta,'locked_cohort':{k:v for k,v in cohort.items() if k!='records'},
        'clean_full_reference':clean,'methods':{},
        'quality_population':'clean-correct Fake only; PSNR null denotes infinity',
        'postprocessing_source_sha256':{n:sha(Path(__file__).parent/n) for n in (
            'summarize_external_full.py','summarize_final.py','analyze_by_video.py')},
        'evidence_sha256':{'results.json':sha(folder/'results.json')}}
    identity = None
    frequency_rows = {}
    for method in METHODS:
        path = folder/(method+'_per_frame.jsonl')
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        ids = [r['record_id_sha256_16'] for r in rows]
        assert len(ids)==len(set(ids))==len(expected) and set(ids)==set(expected)
        assert Counter(r['label'] for r in rows)=={0:cohort['real'],1:cohort['fake']}
        current = [(r['record_id_sha256_16'],r['clean_score']) for r in rows]
        if identity is None:
            identity = current
        else:
            assert current==identity
        for r in rows:
            original = expected[r['record_id_sha256_16']]
            assert (r['label'],r['video'],r['manipulation'])==(original['label'],original['video'],original['manipulation'])
            eligible = r['label']==1 and r['clean_score']>=.5
            assert r['attack_applied']==eligible
            assert r['source_cluster']==dataset+'-video:'+r['video']
            if not eligible:
                assert r['linf']==r['dct_linf']==r['dct_l2']==0
                assert r['clean_score']==r['attacked_score']
            if method in ('fgsm','pgd'):
                assert r['linf']<=meta['settings']['epsilon']+1e-6
            else:
                assert r['dct_'+meta['settings']['frequency_norm']]<=meta['settings']['frequency_epsilon']+1e-6
            if method in ('pgd','jia-faa-reconstruction'):
                assert r['attacked_score']<=r['clean_score']+1e-7
        s = final['results'][method]
        assert s['total_frames']==cohort['frames'] and s['fake_frames']==cohort['fake']
        assert abs(s['clean_frame_accuracy']-clean['accuracy'])<=clean['tolerance']
        assert abs(s['clean_frame_auc']-clean['auc'])<=clean['tolerance']
        eligible = [r for r in rows if r['attack_applied']]
        flips = sum(r['attacked_score']<.5 for r in eligible)
        assert len(eligible)==s['eligible_clean_correct_fake'] and flips==s['fake_to_real_flips']
        analysis_path = folder/(method+'_video_analysis.json')
        analysis = read(analysis_path)
        assert analysis['frame_counts']['fake_to_real_flips']==flips
        assert analysis['frame_counts']['eligible_clean_correct_fake']==len(eligible)
        assert analysis['video_count']==cohort['video_records']
        output['methods'][method] = {'summary':s,'video_analysis':analysis,
            'eligible_quality_and_diagnostics':diagnostics(eligible),
            'nonzero_eligible_frames':sum(r['linf']>0 for r in eligible)}
        output['evidence_sha256'][path.name]=sha(path)
        output['evidence_sha256'][analysis_path.name]=sha(analysis_path)
        if method in ('frequency-init-control','jia-faa-reconstruction'):
            frequency_rows[method]=rows
    output['frequency_paired_comparison']=paired_frequency(frequency_rows['jia-faa-reconstruction'],frequency_rows['frequency-init-control'])
    output['audits_passed']=['full prelocked cohort/config/checkpoint identity',
        'same core attack/quality/diagnostics code as full DFDC', 'source snapshot hashes',
        'unique records and expected labels/video/manipulation', 'paired clean scores/order',
        'Real and baseline false-negative Fake unchanged','final pixel/frequency norm bounds',
        'PGD/FAA best iterate not worse than clean','clean reference continuity',
        'summary/per-frame counts and video counts agree']
    return output


def report(path, dataset, data):
    s=data['methods']['jia-faa-reconstruction']['summary']
    cohort=data['locked_cohort']
    lines=[f'# EXP-004 — Full {LABELS[dataset]}','',
        f"Full processed test manifest: {cohort['frames']:,} frames; {cohort['real']:,} Real, {cohort['fake']:,} Fake; {cohort['video_records']:,} video/sequence records.",'',
        f"FAA reconstruction: **{s['fake_to_real_flips']:,}/{s['eligible_clean_correct_fake']:,} clean-correct Fake → Real; ASR {100*s['asr_fake_given_clean_correct']:.2f}%.**",'',
        f"Clean frame AUC={s['clean_frame_auc']:.6f}, ACC={s['clean_frame_accuracy']:.6f}; clean gate passed with tolerance 0.001. Historical baseline is a continuity check, not an exact match to all paper results.",'',
        'Frozen EXP-002 checkpoint, input preprocessing, attack settings, batch size and seed transfer unchanged from full DFDC. All test frames are evaluated; only clean-correct Fake frames are attacked. Real and baseline false-negative Fake frames remain unchanged. No training or test-set parameter selection.','',
        '| Method | Flips / eligible | ASR | Attacked-Fake / clean-Real AUC |','|---|---:|---:|---:|']
    for method in METHODS:
        r=data['methods'][method]['summary']
        lines.append(f"| {method} | {r['fake_to_real_flips']:,}/{r['eligible_clean_correct_fake']:,} | {100*r['asr_fake_given_clean_correct']:.2f}% | {r['attacked_fake_clean_real_frame_auc']:.6f} |")
    v=data['methods']['jia-faa-reconstruction']['video_analysis']
    ci=v['frame_asr_95pct_cluster_bootstrap']
    paired=data['frequency_paired_comparison']
    lines += ['',f"FAA frame ASR 95% video/sequence-cluster bootstrap interval: {100*ci[0]:.2f}–{100*ci[1]:.2f}%; 1,000 replicates. Exploratory: shared source/identity linkage is unavailable; frames and sequences can be dependent.",
        f"Video/sequence-level FAA ASR: {v['video_counts']['fake_to_real_flips']:,}/{v['video_counts']['eligible_clean_correct_fake']:,} = {100*v['video_fake_asr']:.2f}% (mean score across selected frames).",
        f"Paired FAA minus initialization-control ASR: {100*paired['asr_difference_faa_minus_control']:.2f} percentage points; paired flip table and bootstrap interval are in the evidence JSON.",'',
        '| Method | Mean finite PSNR (dB) | Mean SSIM | Runtime (s) |','|---|---:|---:|---:|']
    for method in METHODS:
        m=data['methods'][method]; q=m['eligible_quality_and_diagnostics']
        lines.append(f"| {method} | {q['psnr_db'].get('mean',0):.3f} | {q['ssim'].get('mean',0):.6f} | {m['summary']['seconds']:.2f} |")
    lines += ['', 'Quality conditions on clean-correct Fake. Infinite PSNR for unchanged images is excluded from finite averages; counts and extrema are preserved in JSON. SSIM does not establish imperceptibility. Pixel L∞=4/255 and global DCT L∞=0.1 have different units; ASR does not fairly rank their matched strength. FAA: block8, energy-proportion M, P-step0.01, 10 updates, first-evasion stopping; PGD: alpha1/255, 10 updates, five trajectories. Seed1024, batch32.','',
        '| FAA outcome | Frames | Gate MAE | Attention MAE | Variance MAE |','|---|---:|---:|---:|---:|']
    for outcome,g in v['mechanism_success_vs_failure'].items():
        lines.append(f"| {outcome} | {g['frames']:,} | {g['gates_mae_mean']:.6f} | {g['attention_mae_mean']:.6f} | {g['variance_mae_mean']:.6f} |")
    lines += ['', 'FAA remains an explicit reconstruction of Jia, not author-verified exact reproduction. Diagnostics are descriptive associations, without causal attribution to WGSA. Evaluation covers cropped decoded inputs, not re-encoded videos. Dataset ASRs condition on different clean-correct populations and should not be interpreted as a pure dataset-difficulty ranking. EXP-005 remains outside scope.','',
        f"Evidence: [compact JSON](full-{dataset}-evaluation.json), [locked config](../code/configs/final_reconstruction_{dataset}_full.json). Runtime: `exp04-runtime/runs/final_{dataset}_full_reconstruction_001/`; per-frame evidence, source snapshots, examples and analyses stay outside Git. Cohort locked before attack in `exp04-runtime/cohorts/full_{dataset}.json`.",'',
        'All recorded identity, code continuity, eligibility, perturbation-bound and summary consistency audits passed.','']
    path.write_text('\n'.join(lines))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runtime-root',type=Path,required=True)
    p.add_argument('--dataset',choices=LABELS,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    a=p.parse_args()
    data=audit(a.runtime_root,a.dataset)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    target=a.output_dir/f'full-{a.dataset}-evaluation.json'
    target.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
    report(a.output_dir/f'full-{a.dataset}-report.md',a.dataset,data)
    print('EXTERNAL_AUDIT_PASSED '+str(target),flush=True)


if __name__=='__main__':
    main()
