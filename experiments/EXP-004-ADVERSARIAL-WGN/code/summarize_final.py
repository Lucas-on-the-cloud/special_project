"""Audit paired final outputs and export compact, face-free EXP-004 evidence.

Run analyze_by_video.py for each method first. No attack parameters are chosen
here. All quality/diagnostic summaries below condition on clean-correct Fake.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np

METHODS = ('fgsm', 'pgd', 'frequency-init-control', 'jia-faa-reconstruction')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def describe(values):
    values = [v for v in values if v is not None]
    if not values:
        return {'finite_count': 0}
    x = np.asarray(values, dtype=float)
    if not np.isfinite(x).all():
        raise AssertionError('Nonfinite summary input')
    return dict(finite_count=len(x), mean=float(x.mean()), median=float(np.median(x)),
                p05=float(np.quantile(x, .05)), p95=float(np.quantile(x, .95)),
                minimum=float(x.min()), maximum=float(x.max()))


def diagnostics(rows):
    result = {'frames': len(rows)}
    for field in ('linf', 'dct_linf', 'dct_l2', 'mse', 'psnr_db', 'ssim',
                  'attention_mae', 'gates_mae'):
        result[field] = describe([r[field] for r in rows])
    # Stored ordering follows the frozen victim's four Haar kernels.
    result['bands'] = {}
    for field in ('mean', 'abs_mean', 'variance', 'energy', 'gates'):
        result['bands'][field] = {
            'clean_mean': np.mean([r[field+'_clean'] for r in rows], axis=0).tolist() if rows else None,
            'absolute_drift_mean': np.mean([
                np.abs(np.array(r[field+'_attacked'])-r[field+'_clean']) for r in rows
            ], axis=0).tolist() if rows else None}
    return result


def paired_frequency(rows, control):
    eligible = [i for i,r in enumerate(rows) if r['label']==1 and r['clean_score']>=.5]
    cells = Counter()
    clusters = {}
    for i in eligible:
        a = rows[i]['attacked_score'] < .5
        b = control[i]['attacked_score'] < .5
        cells[f'FAA_{int(a)}_control_{int(b)}'] += 1
        cluster = rows[i]['source_cluster']
        n, delta = clusters.get(cluster, (0,0))
        clusters[cluster] = (n+1, delta+int(a)-int(b))
    result = {'eligible_frames':len(eligible), 'paired_flip_table':dict(cells),
              'asr_difference_faa_minus_control':sum(v[1] for v in clusters.values())/len(eligible) if eligible else None}
    if len(clusters)>1:
        values = np.array([clusters[k] for k in sorted(clusters)])
        rng = np.random.default_rng(1024)
        draws = rng.integers(0,len(values),size=(1000,len(values)))
        totals = values[draws].sum(axis=1)
        result['difference_95pct_cluster_bootstrap'] = np.quantile(totals[:,1]/totals[:,0],[.025,.975]).tolist()
        result['bootstrap_seed'] = 1024
        result['bootstrap_repeats'] = 1000
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.runtime_root
    output = {'scope':'frozen WGN, fake-evasion, explicit FAA reconstruction; single locked seed/config',
              'postprocessing_source_sha256':{name:sha(Path(__file__).parent/name)
                  for name in ('summarize_final.py','analyze_by_video.py')},
              'quality_population':'clean-correct Fake, including zero changes if retained',
              'psnr_note':'null means infinity for unchanged images; finite-count excludes these',
              'bands_note':'array ordering is the frozen victim Haar kernel order',
              'datasets':{}}
    for dataset in ('ffpp','dfdc'):
        folder = root/'runs'/f'final_{dataset}_reconstruction_001'
        final = read(folder/'results.json')
        assert final['complete'] is True
        meta = final['metadata']
        cohort = read(root/'cohorts'/f'final_{dataset}.json')
        assert meta['cohort_fingerprint']==cohort['cohort_fingerprint']
        assert meta['protocol_lock_sha256']==cohort['protocol_lock_sha256']
        assert meta['checkpoint_sha256']==cohort['checkpoint_sha256']
        expected = {hashlib.sha256(r['path'].encode()).hexdigest()[:16]:r for r in cohort['records']}
        assert len(expected)==cohort['frames']
        result = {'metadata':meta,'locked_cohort':{k:v for k,v in cohort.items() if k!='records'},
                  'clean_full_reference':read(root/'runs'/('clean_ffpp_c23.json' if dataset=='ffpp' else 'clean_dfdc.json')),
                  'methods':{},'evidence_sha256':{'results.json':sha(folder/'results.json')}}
        all_rows = {}
        for method in METHODS:
            path = folder/(method+'_per_frame.jsonl')
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            ids = [r['record_id_sha256_16'] for r in rows]
            assert len(ids)==len(set(ids))==len(expected) and set(ids)==set(expected)
            assert Counter(r['label'] for r in rows)==Counter(r['label'] for r in cohort['records'])
            for r in rows:
                identity = expected[r['record_id_sha256_16']]
                assert (r['label'],r['video'],r['manipulation'])==(identity['label'],identity['video'],identity['manipulation'])
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
            if all_rows:
                first = all_rows['fgsm']
                assert [(r['record_id_sha256_16'],r['clean_score']) for r in rows]==[(r['record_id_sha256_16'],r['clean_score']) for r in first]
            eligible = [r for r in rows if r['attack_applied']]
            analysis_path = folder/(method+'_video_analysis.json')
            result['methods'][method] = {
                'summary':final['results'][method], 'video_analysis':read(analysis_path),
                'eligible_quality_and_diagnostics':diagnostics(eligible),
                'saved_example_first_eligible':{k:eligible[0][k] for k in (
                    'record_id_sha256_16','clean_score','attacked_score')} if eligible else None,
                'nonzero_eligible_frames':sum(r['linf']>0 for r in eligible)}
            if method=='jia-faa-reconstruction':
                result['methods'][method]['band_drift_by_manipulation_and_outcome'] = {
                    group:{outcome:diagnostics([r for r in eligible if r['manipulation']==group
                        and (r['attacked_score']<.5)==success])['bands']
                        for outcome,success in [('success',True),('failure',False)]}
                    for group in sorted({r['manipulation'] for r in eligible})}
            result['evidence_sha256'][path.name] = sha(path)
            result['evidence_sha256'][analysis_path.name] = sha(analysis_path)
            all_rows[method] = rows
        result['frequency_paired_comparison'] = paired_frequency(all_rows['jia-faa-reconstruction'],all_rows['frequency-init-control'])
        result['audits_passed'] = ['prelocked identities/config', 'no duplicate records',
            'paired clean scores/order', 'Real and baseline false negatives unchanged',
            'final perturbation bounds', 'PGD/FAA best iterate not worse than clean']
        output['datasets'][dataset] = result
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    print(str(args.output))


if __name__=='__main__':
    main()
