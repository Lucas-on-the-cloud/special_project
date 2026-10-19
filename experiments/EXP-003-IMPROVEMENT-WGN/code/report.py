from __future__ import annotations

import json
from pathlib import Path

RUNS=Path('C:/sp/runs/wgn_overnight')
METHODS=['baseline','gradient','curriculum','temporal_control','temporal',
         'degradation_control','degradation_consistency']
LABELS={'baseline':'WGN reproduced reference (EXP-002)'}


def generate():
    rows=[]
    results={}
    for method in METHODS:
        path=RUNS/f'{method}_final'/'evaluation.json'
        if path.exists():
            results[method]=json.loads(path.read_text())['datasets']
    official={}
    for method in METHODS:
        path=RUNS/f'{method}_final'/'evaluation-celebdf-official-direct.json'
        if path.exists():
            official[method]=json.loads(path.read_text())['metrics']
        else:
            value=results.get(method,{}).get('Celeb-DF-v2 official-direct')
            if value:
                official[method]=value
    lines=['# WGN results','',
           'AUC values below are percentages. Missing cells are pending, not zero. '
           'Synthetic smoke-test numbers and 5-epoch pilots are excluded.','',
           '| Model | FF++ c23 frame AUC | FF++ c40 frame AUC | Celeb-DF v2 official-direct video AUC | DFDC video AUC | WildDeepfake video AUC |',
           '|---|---|---|---|---|---|']
    for method in METHODS:
        fields=[]
        for name in ['FF++ c23','FF++ c40']:
            value=results.get(method,{}).get(name,{})
            fields.append(f'{100*value["auc"]:.2f}' if 'auc' in value else 'pending')
        official_value=official.get(method,{})
        fields.append(f'{100*official_value["video_auc"]:.2f}' if 'video_auc' in official_value else 'pending')
        for name in ['DFDC','WildDeepfake']:
            value=results.get(method,{}).get(name,{})
            fields.append(f'{100*value["video_auc"]:.2f}' if 'video_auc' in value else 'pending')
        lines.append('| '+LABELS.get(method,method)+' | '+' | '.join(fields)+' |')
    lines+=['','Celeb-DF v2 uses the authors\' MP4 archive, the official 518-video test list, '
            'uniform 32-frame sampling, and the same WGN MTCNN crop code. The earlier DeepfakeBench '
            'measurements remain archived for provenance and are excluded from current comparisons.','']
    lines+=['','Selection check: Celeb-DF video AUC gain >=2 percentage points; '
            'FF++ c23 frame AUC loss <=1 percentage point, relative to the EXP-002 reproduced WGN reference.','']
    baseline=results.get('baseline',{})
    baseline_official=official.get('baseline',{})
    for method in ['gradient','curriculum','temporal','degradation_control','degradation_consistency']:
        values=results.get(method,{})
        direct=official.get(method,{})
        if 'video_auc' in baseline_official and 'video_auc' in direct and 'FF++ c23' in baseline and 'FF++ c23' in values:
            gain=100*(direct['video_auc']-baseline_official['video_auc'])
            drop=100*(baseline['FF++ c23']['auc']-values['FF++ c23']['auc'])
            lines.append(f'- {method}: Celeb-DF gain {gain:+.2f} pp; c23 loss {drop:+.2f} pp; '
                         f'{"meets" if gain>=2 and drop<=1 else "does not meet"} initial criterion.')
    lines+=['','## Cross-manipulation follow-up','',
            '| Method/train group | Mean frame AUC including diagonal | Unseen mean frame AUC |',
            '|---|---|---|']
    for path in sorted(RUNS.glob('cross_*_final/cross_manipulation.json')):
        value=json.loads(path.read_text())
        lines.append(f'| {path.parent.name} | {100*value["average_auc_including_diagonal"]:.2f} | '
                     f'{100*value["average_unseen_auc"]:.2f} |')
    (RUNS/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':
    generate()
