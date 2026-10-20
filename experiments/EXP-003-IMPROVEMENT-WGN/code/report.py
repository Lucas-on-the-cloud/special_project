from __future__ import annotations

import json
from pathlib import Path


RUNS = Path('C:/sp/runs/wgn_overnight')
METHODS = ['baseline', 'gradient', 'curriculum', 'temporal_control', 'temporal',
           'degradation_control', 'degradation_consistency']
CANDIDATES = METHODS[1:]
LABELS = {'baseline': 'WGN reproduced reference (EXP-002, RTX 5060 Ti)',
          'temporal_control': 'temporal sampling control'}
HEADLINE_METRICS = [
    ('FF++ c23', 'auc'),
    ('Celeb-DF v2 official-direct', 'video_auc'),
    ('DFDC', 'video_auc'),
    ('WildDeepfake', 'video_auc'),
]
TARGETS = [
    ('FF++ c40', 'auc', 'FF++ c40 frame'),
    ('FaceShifter c23 (held-out)', 'auc', 'FaceShifter c23 frame'),
    ('FaceShifter c40 (held-out)', 'auc', 'FaceShifter c40 frame'),
    ('Celeb-DF v2 official-direct', 'video_auc', 'Celeb-DF video'),
    ('DFDC', 'video_auc', 'DFDC video'),
    ('WildDeepfake', 'video_auc', 'WildDeepfake video'),
]


def load_results():
    results, official = {}, {}
    for method in METHODS:
        path = RUNS / f'{method}_final' / 'evaluation.json'
        if path.exists():
            results[method] = json.loads(path.read_text())['datasets']
        direct = RUNS / f'{method}_final' / 'evaluation-celebdf-official-direct.json'
        if direct.exists():
            official[method] = json.loads(direct.read_text())['metrics']
        else:
            value = results.get(method, {}).get('Celeb-DF-v2 official-direct')
            if value:
                official[method] = value
    return results, official


def metric(results, official, method, dataset, key):
    if dataset == 'Celeb-DF v2 official-direct':
        return official.get(method, {}).get(key)
    return results.get(method, {}).get(dataset, {}).get(key)


def selection(results, official):
    baseline_c23 = metric(results, official, 'baseline', 'FF++ c23', 'auc')
    baseline_targets = [metric(results, official, 'baseline', dataset, key)
                        for dataset, key, _ in TARGETS]
    decisions = {}
    if baseline_c23 is None or any(value is None for value in baseline_targets):
        return decisions, []
    completed = {}
    for method in CANDIDATES:
        c23 = metric(results, official, method, 'FF++ c23', 'auc')
        values = [metric(results, official, method, dataset, key) for dataset, key, _ in TARGETS]
        if c23 is None or any(value is None for value in values):
            decisions[method] = {'status': 'pending'}
            continue
        gains = [100 * (value - baseline) for value, baseline in zip(values, baseline_targets)]
        c23_loss = 100 * (baseline_c23 - c23)
        improved = sum(gain >= .5 for gain in gains)
        worst_regression = max(0., -min(gains))
        strict = gains[3] >= 2 and c23_loss <= 1 and improved >= 2 and worst_regression <= 2
        diagnostic = c23_loss <= 1 and improved >= 2 and worst_regression <= 2
        decisions[method] = {'status': 'strict finalist' if strict else
                             'diagnostic eligible' if diagnostic else 'not retained',
                             'c23_loss': c23_loss, 'gains': gains, 'improved': improved,
                             'worst_regression': worst_regression, 'mean_gain': sum(gains) / len(gains)}
        completed[method] = gains
    pareto = []
    for method, gains in completed.items():
        dominated = any(other != method and all(a >= b for a, b in zip(other_gains, gains))
                        and any(a > b for a, b in zip(other_gains, gains))
                        for other, other_gains in completed.items())
        if not dominated:
            pareto.append(method)
            decisions[method]['pareto'] = True
    strict = [method for method in pareto if decisions[method]['status'] == 'strict finalist']
    recommended = strict or [method for method in pareto
                             if decisions[method]['status'] == 'diagnostic eligible']
    recommended.sort(key=lambda method: decisions[method]['mean_gain'], reverse=True)
    return decisions, recommended


def generate():
    results, official = load_results()
    decisions, recommended = selection(results, official)
    lines = ['# WGN results', '',
             'AUC values below are percentages. Missing cells are pending, not zero. '
             'Synthetic smoke-test numbers and 5-epoch pilots are excluded.', '',
             '| Model | FF++ c23 frame | Celeb-DF official video | DFDC video | WildDeepfake video |',
             '|---|---:|---:|---:|---:|']
    for method in METHODS:
        fields = []
        for dataset, key in HEADLINE_METRICS:
            value = metric(results, official, method, dataset, key)
            fields.append(f'{100 * value:.2f}' if value is not None else 'pending')
        label = LABELS.get(method, method)
        if method in recommended:
            label = f'**{label} — selected potential candidate**'
            fields = [f'**{value}**' for value in fields]
        lines.append('| ' + label + ' | ' + ' | '.join(fields) + ' |')
    lines += ['', "Celeb-DF v2 uses the authors' MP4 archive, the official 518-video test list, "
              'uniform 32-frame sampling, and the same WGN MTCNN crop code. The earlier DeepfakeBench '
              'measurements remain archived for provenance and are excluded from current comparisons. '
              'FF++ c40 and FaceShifter held-out checks remain in the machine-readable selection record '
              'but are omitted here because they are not independently trained Table 1 reproductions.', '']
    if recommended:
        lines += ['> **Selected potential candidate:** ' +
                  ', '.join(LABELS.get(method, method) for method in recommended) +
                  '. It passes the locked generalization criteria and is queued for cross-manipulation validation.', '']
    lines += [
              '## Candidate selection', '',
              'A strict finalist must gain at least 2 pp on Celeb-DF, lose no more than 1 pp on FF++ c23, '
              'improve at least two generalization targets by 0.5 pp, and regress by no more than 2 pp on '
              'any generalization target. If none passes, a non-dominated method meeting the last three '
              'conditions is marked diagnostic eligible.', '',
              '| Method | c23 loss | Celeb gain | Improved targets | Worst target regression | Pareto | Decision |',
              '|---|---:|---:|---:|---:|---:|---|']
    selection_complete = bool(decisions) and all(
        decisions.get(method, {}).get('status') != 'pending' for method in CANDIDATES)
    selection_payload = {
        'schema_version': 1,
        'status': 'complete' if selection_complete else 'pending',
        'reference': 'baseline_final (EXP-002 reproduced WGN)',
        'targets': [label for _, _, label in TARGETS],
        'thresholds_percentage_points': {
            'minimum_celeb_df_gain_for_strict_finalist': 2.0,
            'maximum_ffpp_c23_loss': 1.0,
            'minimum_gain_count': 2,
            'gain_threshold_per_target': 0.5,
            'maximum_regression_on_any_target': 2.0,
        },
        'decisions': decisions,
        'recommended_cross_manipulation': recommended if selection_complete else [],
    }
    (RUNS / 'SELECTION.json').write_text(
        json.dumps(selection_payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    for method in CANDIDATES:
        decision = decisions.get(method, {'status': 'pending'})
        if decision['status'] == 'pending':
            lines.append(f'| {LABELS.get(method, method)} | pending | pending | pending | pending | pending | pending |')
            continue
        fields = [LABELS.get(method, method), f"{decision['c23_loss']:+.2f}",
                  f"{decision['gains'][3]:+.2f}", f"{decision['improved']}/6",
                  f"{decision['worst_regression']:.2f}",
                  'yes' if decision.get('pareto') else 'no', decision['status']]
        if method in recommended:
            fields = [f'**{value}**' for value in fields]
        lines.append('| ' + ' | '.join(fields) + ' |')
    if recommended:
        lines += ['', '**Recommended cross-manipulation follow-up:** ' +
                  ', '.join(LABELS.get(method, method) for method in recommended) + '.', '']
    elif decisions and all(value['status'] != 'pending' for value in decisions.values()):
        lines += ['', '**Recommended cross-manipulation follow-up:** none under the locked criteria.', '']
    else:
        lines += ['', '**Recommended cross-manipulation follow-up:** pending completion of the common sweep.', '']
    lines += ['## Cross-manipulation follow-up', '',
              '| Method/train group | Mean frame AUC including diagonal | Unseen mean frame AUC |',
              '|---|---:|---:|']
    for path in sorted(RUNS.glob('cross_*_final/cross_manipulation.json')):
        value = json.loads(path.read_text())
        lines.append(f'| {path.parent.name} | {100 * value["average_auc_including_diagonal"]:.2f} | '
                     f'{100 * value["average_unseen_auc"]:.2f} |')
    (RUNS / 'RESULTS.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    generate()
