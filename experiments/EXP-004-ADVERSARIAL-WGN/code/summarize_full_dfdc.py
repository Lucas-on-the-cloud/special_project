"""Audit the full DFDC run and compare it with the preserved 2,000-frame run.

Requires results.json/complete=true and analyze_by_video.py outputs for all
methods. Exports compact evidence and a Vietnamese report without face media.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from summarize_final import METHODS, diagnostics, paired_frequency, read, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime_root
    folder = runtime/'runs/final_dfdc_full_reconstruction_001'
    final = read(folder/'results.json')
    initial = read(runtime/'runs/final_dfdc_reconstruction_001/results.json')
    cohort = read(runtime/'cohorts/full_dfdc.json')
    clean = read(runtime/'runs/clean_dfdc.json')
    assert final['complete'] is True and initial['complete'] is True
    meta = final['metadata']
    assert meta['settings']=={**initial['metadata']['settings'],'max_samples':0}
    assert meta['cohort_fingerprint']==meta['full_cohort_fingerprint']==cohort['cohort_fingerprint']==clean['portable_cohort_fingerprint']
    assert meta['protocol_lock_sha256']==cohort['protocol_lock_sha256']
    assert meta['checkpoint_sha256']==cohort['checkpoint_sha256']==clean['checkpoint_sha256']==initial['metadata']['checkpoint_sha256']
    assert meta['manifest_sha256']==cohort['manifest_sha256']==clean['manifest_sha256']
    assert clean['passed'] and meta['selected_frames']==cohort['frames']==132116
    for name,expected in initial['metadata']['source_sha256'].items():
        assert meta['source_sha256'][name]==expected, ('Changed source',name)
    expected = {hashlib.sha256(r['path'].encode()).hexdigest()[:16]:r for r in cohort['records']}
    assert len(expected)==cohort['frames']
    output = {
        'scope':'full restored DFDC test manifest; frozen WGN; explicit FAA reconstruction',
        'metadata':meta, 'locked_cohort':{k:v for k,v in cohort.items() if k!='records'},
        'clean_full_reference':clean,
        'quality_population':'clean-correct Fake only; PSNR null denotes infinity',
        'comparison_note':'same settings/seed, larger cohort changes batch composition and RNG sequence; not a paired change of attack algorithm',
        'postprocessing_source_sha256':{name:sha(Path(__file__).parent/name) for name in (
            'summarize_full_dfdc.py','summarize_final.py','analyze_by_video.py')},
        'evidence_sha256':{'results.json':sha(folder/'results.json')},
        'methods':{}, 'initial_cohort_comparison':{}}
    all_rows = {}
    first_identity = None
    for method in METHODS:
        path = folder/(method+'_per_frame.jsonl')
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        ids = [r['record_id_sha256_16'] for r in rows]
        assert len(ids)==len(set(ids))==len(expected) and set(ids)==set(expected)
        assert Counter(r['label'] for r in rows)=={0:63265,1:68851}
        identity = [(r['record_id_sha256_16'],r['clean_score']) for r in rows]
        if first_identity is None:
            first_identity = identity
        else:
            assert identity==first_identity
        for r in rows:
            original = expected[r['record_id_sha256_16']]
            assert (r['label'],r['video'],r['manipulation'])==(original['label'],original['video'],original['manipulation'])
            eligible = r['label']==1 and r['clean_score']>=.5
            assert r['attack_applied']==eligible
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
        assert abs(s['clean_frame_accuracy']-clean['accuracy'])<=clean['tolerance']
        assert abs(s['clean_frame_auc']-clean['auc'])<=clean['tolerance']
        eligible = [r for r in rows if r['attack_applied']]
        flips = sum(r['attacked_score']<.5 for r in eligible)
        assert len(eligible)==s['eligible_clean_correct_fake'] and flips==s['fake_to_real_flips']
        analysis_path = folder/(method+'_video_analysis.json')
        analysis = read(analysis_path)
        assert analysis['frame_counts']['fake_to_real_flips']==flips
        output['methods'][method] = {
            'summary':s,'video_analysis':analysis,
            'eligible_quality_and_diagnostics':diagnostics(eligible),
            'nonzero_eligible_frames':sum(r['linf']>0 for r in eligible)}
        before = initial['results'][method]
        output['initial_cohort_comparison'][method] = {
            'initial_frames':before['total_frames'],
            'initial_eligible':before['eligible_clean_correct_fake'],
            'initial_flips':before['fake_to_real_flips'],
            'initial_asr':before['asr_fake_given_clean_correct'],
            'full_frames':s['total_frames'],'full_eligible':len(eligible),'full_flips':flips,
            'full_asr':s['asr_fake_given_clean_correct'],
            'full_minus_initial_asr':s['asr_fake_given_clean_correct']-before['asr_fake_given_clean_correct']}
        output['evidence_sha256'][path.name]=sha(path)
        output['evidence_sha256'][analysis_path.name]=sha(analysis_path)
        if method in ('frequency-init-control','jia-faa-reconstruction'):
            all_rows[method]=rows
    output['frequency_paired_comparison']=paired_frequency(all_rows['jia-faa-reconstruction'],all_rows['frequency-init-control'])
    output['audits_passed']=['full prelocked cohort/config identity','same attack/evaluation source as initial run',
        'unique records and expected labels/video/manipulation','paired clean scores/order across methods',
        'Real and baseline false-negative Fake unchanged','final pixel/frequency norm bounds',
        'PGD/FAA best iterate not worse than clean','full clean continuity','summary/per-frame counts agree']
    args.output_dir.mkdir(parents=True,exist_ok=True)
    target = args.output_dir/'full-dfdc-evaluation.json'
    target.write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    write_report(args.output_dir/'full-dfdc-report.md',output)
    print(target)


def write_report(path, data):
    methods=data['methods']
    faa=methods['jia-faa-reconstruction']
    s=faa['summary']; v=faa['video_analysis']
    ci=v['frame_asr_95pct_cluster_bootstrap']
    paired=data['frequency_paired_comparison']
    lines=['# EXP-004 — Full DFDC test evaluation','',
        'Ngày chạy: 2026-11-15, Asia/Taipei. Đây là toàn bộ test manifest đã restore, không phải toàn bộ kho video DFDC gốc. Không gộp train/validation.','',
        f"**FAA reconstruction làm {s['fake_to_real_flips']:,}/{s['eligible_clean_correct_fake']:,} Fake clean-correct chuyển thành Real: ASR {100*s['asr_fake_given_clean_correct']:.2f}%.**",'',
        '## Phạm vi và tính liên tục','',
        '- 132.116 frames: 63.265 Real và 68.851 Fake. Cohort fingerprint, manifest và checkpoint khớp clean gate đã qua kiểm tra.',
        '- Checkpoint EXP-002 frozen; preprocessing và bốn phương pháp giữ nguyên. Config mới chỉ đổi max_samples từ 2000 sang 0. Danh sách cohort và config được khóa trước attack.',
        f"- Có {s['eligible_clean_correct_fake']:,} Fake nhận diện đúng trước attack; {68851-s['eligible_clean_correct_fake']:,} baseline false negatives giữ nguyên và không tính là attack success. Toàn bộ Real giữ nguyên.",
        f"- Clean ACC={s['clean_frame_accuracy']:.6f}, AUC={s['clean_frame_auc']:.6f}; đạt clean-reference tolerance 0,001.",
        '- DCT attack tác động lên input RGB sau crop/decode; chưa đánh giá tái nén hoặc pipeline video đầu cuối.',
        '- FAA là bản tái dựng theo Jia, chưa xác minh code tác giả. M=energy-proportion; block=8; DCT L∞ epsilon=0,1; P-step=0,01; 10 updates, first-evasion stopping. FGSM/PGD pixel L∞=4/255; PGD alpha=1/255, 10 updates, 5 trajectories. Seed=1024, batch=32.',
        '', '## Kết quả và so sánh cohort ban đầu','',
        '| Method | Full flips / eligible | Full ASR | ASR trên cohort 2.000 ảnh | Full attacked-Fake / clean-Real AUC |',
        '|---|---:|---:|---:|---:|']
    for name,m in methods.items():
        row=m['summary']; old=data['initial_cohort_comparison'][name]
        lines.append(f"| {name} | {row['fake_to_real_flips']:,}/{row['eligible_clean_correct_fake']:,} | {100*row['asr_fake_given_clean_correct']:.2f}% | {100*old['initial_asr']:.2f}% | {row['attacked_fake_clean_real_frame_auc']:.6f} |")
    lines += ['', 'Cùng tham số/seed nhưng thay population sẽ thay batch composition và chuỗi random cho từng ảnh; không coi chênh lệch full/cohort là một phép so sánh paired về thuật toán. Không xếp hạng pixel attacks và FAA như ngân sách tương đương.', '',
        f"FAA ASR 95% video-cluster-bootstrap interval: **{100*ci[0]:.2f}–{100*ci[1]:.2f}%**. Paired FAA/control ASR tăng **{100*paired['asr_difference_faa_minus_control']:.2f} điểm phần trăm**.",
        'Bootstrap 1.000 replicates. DFDC thiếu original-source linkage nên intervals vẫn exploratory; nhiều frames/video không phải các quan sát độc lập.', '',
        f"Video-level FAA: {v['video_counts']['fake_to_real_flips']:,}/{v['video_counts']['eligible_clean_correct_fake']:,}, ASR={100*v['video_fake_asr']:.2f}%, mean score trên toàn bộ frames được chọn của video. Tổng {v['video_count']:,} video records.", '',
        '## Chất lượng ảnh và chi phí','',
        '| Method | PSNR mean (dB) | SSIM mean | Runtime (s) | Peak allocated VRAM (MiB) |',
        '|---|---:|---:|---:|---:|']
    for name,m in methods.items():
        q=m['eligible_quality_and_diagnostics']; row=m['summary']
        lines.append(f"| {name} | {q['psnr_db'].get('mean',0):.3f} | {q['ssim'].get('mean',0):.6f} | {row['seconds']:.2f} | {row['peak_allocated_mib']:.1f} |")
    lines += ['', 'Chất lượng chỉ tổng hợp trên Fake clean-correct; PSNR null nghĩa là vô hạn nếu ảnh không đổi, finite-count có trong JSON. SSIM cao không chứng minh nhiễu không nhìn thấy. Runtime gồm loader, attack, quality, diagnostics và ghi output.', '',
        '## Diagnostics và giới hạn','',
        '| FAA outcome | Frames | Gate MAE mean | Attention MAE mean | Variance MAE mean |',
        '|---|---:|---:|---:|---:|']
    for name,g in v['mechanism_success_vs_failure'].items():
        lines.append(f"| {name} | {g['frames']:,} | {g['gates_mae_mean']:.6f} | {g['attention_mae_mean']:.6f} | {g['variance_mae_mean']:.6f} |")
    lines += ['', 'Đây là liên hệ mô tả ở feature Haar/WGSA; chưa có đối chứng causal và chưa quy nguyên nhân riêng cho WGSA. Một checkpoint, một seed và một cấu hình không bao phủ mọi attack. Không thực hiện training hoặc thay đổi kiến trúc.', '',
        '## Evidence','',
        '- [Full compact evidence](full-dfdc-evaluation.json), [kết quả cohort ban đầu](README.md).',
        '- [Cấu hình full đã khóa](../code/configs/final_reconstruction_dfdc_full.json); [protocol](../docs/V3-PROTOCOL.md).',
        '- Runtime: `exp04-runtime/runs/final_dfdc_full_reconstruction_001/`; có completion marker, per-frame JSONL, source snapshots/diff, metadata, video analyses và ví dụ float32/PNG. Cohort: `exp04-runtime/cohorts/full_dfdc.json`.',
        '- Kiểm tra hậu chạy: cohort/config và source identity, unique records, paired clean scores, Real/false negatives không đổi, bounds, best-iterate và consistency counts đều qua kiểm tra. Ảnh và checkpoint giữ ngoài Git.', '']
    path.write_text('\n'.join(lines))


if __name__=='__main__':
    main()
