"""EXP-004 frozen-WGN evaluation with an explicitly specified FAA reconstruction.

Development attacks use validation data. A final run additionally requires a
JSON protocol lock matching the complete settings returned by settings().
This does not assert author-verified Jia reproduction.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import random
import shutil
import subprocess
import time

import numpy as np
from PIL import Image
import torch
from torch.utils.data import DataLoader, Subset

from diagnostics import WGSADiagnostics, compare_diagnostics
from evaluation_data import DATASETS, load_records, cohort_fingerprint, load_source, ffpp_pair_mapping, source_cluster
from image_quality import image_quality
from jia_faa import FAAConfig, reconstruct_faa, frequency_initialization_control, checked_logits, frequency_norm, require_finite
from paper_aligned_attacks import fgsm_jia_reference, pgd_jia_reference
from run_exp04_v2 import REFERENCE_SHA, file_sha256, select_pilot, evaluation_summary

METHODS = ('clean', 'fgsm', 'pgd', 'frequency-init-control', 'jia-faa-reconstruction')


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def save_example(folder, clean, attacked):
    folder.mkdir(parents=True)
    clean = clean.detach().cpu().numpy().transpose(1,2,0)
    attacked = attacked.detach().cpu().numpy().transpose(1,2,0)
    np.save(folder/'clean.npy',clean)
    np.save(folder/'adversarial.npy',attacked)
    for name,value in [('clean',clean),('adversarial',attacked)]:
        Image.fromarray(np.rint(value*255).clip(0,255).astype(np.uint8)).save(folder/(name+'.png'))
    heat = np.abs(attacked-clean).mean(2)
    scaled = heat/max(float(heat.max()),1e-12)
    color = np.stack([scaled,np.zeros_like(scaled),1-scaled],axis=-1)
    Image.fromarray(np.rint(color*255).astype(np.uint8)).save(folder/'perturbation.png')
    write_json(folder/'description.json',{'pixel_linf':float(np.abs(attacked-clean).max()),
        'png_purpose':'quantized visualization only; float32 arrays preserve evaluated images',
        'heatmap':'per-image normalized mean absolute RGB difference; not actual RGB magnitude'})


def parse():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('repo-root','checkpoint','manifest','data-root','output'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--dataset', choices=DATASETS, required=True)
    p.add_argument('--split', choices=['val','test'], default='val')
    p.add_argument('--purpose', choices=['development','final'], default='development')
    p.add_argument('--compression', choices=['c23','c40'], default='c23')
    p.add_argument('--methods', nargs='+', choices=METHODS, default=['fgsm','pgd'])
    p.add_argument('--epsilon', type=float, default=4/255, help='Pixel L-infinity, FGSM/PGD only')
    p.add_argument('--alpha', type=float, default=1/255, help='Pixel PGD step')
    p.add_argument('--steps', type=int, default=10)
    p.add_argument('--pgd-restarts', type=int, default=5)
    p.add_argument('--frequency-epsilon', type=float)
    p.add_argument('--frequency-step-size', type=float)
    p.add_argument('--frequency-norm', choices=['linf','l2'])
    p.add_argument('--matrix-policy', choices=['energy-proportion','legacy-magnitude-max','uniform'])
    p.add_argument('--block', type=int, default=8)
    p.add_argument('--batch-size', type=int, default=4)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--max-samples', type=int, default=0)
    p.add_argument('--seed', type=int, default=1024)
    p.add_argument('--protocol-lock', type=Path)
    p.add_argument('--clean-reference', type=Path, help='Passed clean gate required for final attacks')
    return p.parse_args()


def settings(args):
    return {key:getattr(args,key) for key in (
        'dataset','split','compression','methods','epsilon','alpha','steps','pgd_restarts',
        'frequency_epsilon','frequency_step_size','frequency_norm','matrix_policy','block',
        'batch_size','workers','max_samples','seed')}


def validate_settings(args):
    if not np.isfinite([args.epsilon,args.alpha]).all() or min(args.epsilon,args.alpha)<=0:
        raise ValueError('Pixel budgets must be finite and positive')
    if min(args.steps,args.pgd_restarts,args.batch_size)<1 or args.workers<0 or args.max_samples<0:
        raise ValueError('Invalid iteration, batch or population setting')
    if args.block<2 or 256%args.block or len(args.methods)!=len(set(args.methods)):
        raise ValueError('Invalid block or duplicated method')
    if args.dataset!='ffpp' and args.compression!='c23':
        raise ValueError('Compression selector is FF++-specific; leave it at c23 for external datasets')
    faa = None
    if any(m in args.methods for m in ('jia-faa-reconstruction','frequency-init-control')):
        if None in (args.frequency_epsilon,args.frequency_step_size,args.frequency_norm,args.matrix_policy):
            raise ValueError('Declare FAA frequency epsilon, step size, norm and M policy explicitly')
        faa = FAAConfig(args.frequency_epsilon,args.frequency_step_size,args.steps,
                        args.frequency_norm,args.matrix_policy,args.block)
        faa.validate()
    attacking = any(name!='clean' for name in args.methods)
    if args.purpose=='development' and args.split=='test' and attacking:
        raise ValueError('Use validation for development attacks; do not tune on final test')
    if args.purpose=='final' and attacking:
        if args.split!='test' or args.protocol_lock is None or args.clean_reference is None:
            raise ValueError('Final attacks require test split, protocol lock and passed clean reference')
        if json.loads(args.protocol_lock.read_text())!=settings(args):
            raise ValueError('CLI differs from the locked protocol')
    return faa


def main():
    args = parse()
    faa = validate_settings(args)
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA required for WGN evaluation')
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    checkpoint_sha = file_sha256(args.checkpoint)
    if checkpoint_sha != REFERENCE_SHA:
        raise ValueError('Frozen EXP-002 checkpoint checksum mismatch')
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    torch.set_num_threads(4)
    torch.backends.cudnn.benchmark = False
    load_source(args.repo_root)
    from wgn.model import WaveletGuidedNetwork
    from wgn.data import FaceForensicsJsonDataset
    payload = torch.load(args.checkpoint, map_location='cpu', weights_only=False)
    cfg = payload['config']['model']
    model = WaveletGuidedNetwork(pretrained=False, backbone_name=cfg['backbone'],gate_hidden_dim=cfg['gate_hidden_dim'])
    model.load_state_dict(payload['model'],strict=True)
    model = model.cuda().eval().requires_grad_(False)
    records = load_records(args.repo_root,args.manifest,args.data_root,payload['config'],args.dataset,args.split,args.compression)
    pair_mapping = ffpp_pair_mapping(args.repo_root,args.split) if args.dataset=='ffpp' else {}
    full_identity = cohort_fingerprint(records,args.data_root)
    if args.purpose=='final' and any(m!='clean' for m in args.methods):
        reference = json.loads(args.clean_reference.read_text())
        if (not reference.get('passed') or reference.get('checkpoint_sha256')!=checkpoint_sha
                or reference.get('portable_cohort_fingerprint')!=full_identity
                or reference.get('manifest_sha256')!=file_sha256(args.manifest)):
            raise ValueError('Clean gate does not identify this exact checkpoint/cohort/manifest')
    indices = select_pilot(records,args.max_samples,args.seed)
    chosen = [records[i] for i in indices]
    batches = DataLoader(Subset(FaceForensicsJsonDataset(records,train=False),indices),
                         batch_size=args.batch_size,shuffle=False,num_workers=args.workers,pin_memory=True)
    args.output.mkdir(parents=True)
    git_commit = subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.repo_root,text=True).strip()
    source_diff = subprocess.check_output(['git','diff','--binary'],cwd=args.repo_root)
    (args.output/'source.patch').write_bytes(source_diff)
    # Include untracked new implementation files in the source identity too.
    source_hashes = {p.name:file_sha256(p) for p in Path(__file__).parent.glob('*.py')}
    snapshot=args.output/'source'
    snapshot.mkdir()
    for path in Path(__file__).parent.glob('*.py'):
        shutil.copyfile(path,snapshot/path.name)
    for name in ('JIA-ALGORITHM-SPEC.md','V3-PROTOCOL.md'):
        shutil.copyfile(Path(__file__).parent.parent/'docs'/name,snapshot/name)
    metadata = {'experiment':'EXP-004-V3','settings':settings(args),'purpose':args.purpose,
        'checkpoint_sha256':checkpoint_sha,'manifest_sha256':file_sha256(args.manifest),
        'cohort_fingerprint':cohort_fingerprint(chosen,args.data_root),'full_cohort_fingerprint':full_identity,
        'selected_frames':len(indices),'git_commit':git_commit,'source_sha256':source_hashes,
        'protocol_lock_sha256':file_sha256(args.protocol_lock) if args.protocol_lock else None,
        'clean_reference_sha256':file_sha256(args.clean_reference) if args.clean_reference else None,
        'packages':{n:importlib.metadata.version(n) for n in ['torch','torchvision','timm','numpy','scikit-learn','Pillow','PyYAML']},
        'python':platform.python_version(),'gpu':torch.cuda.get_device_name(0),
        'preprocessing':'EXP-002 RGB resize 256x256 ToTensor; no normalization/augmentation',
        'scope':'clean-correct Fake attacked; all Real and clean false-negative Fake unchanged',
        'threshold':.5,'faa':asdict(faa) if faa else None,
        'faa_fidelity':'explicit reconstruction; M/norm/feasibility choices not author-verified',
        'ssim':'Gaussian 11x11 sigma1.5, valid window, population covariance, RGB mean, range1',
        'psnr_identical_images':'null denotes positive infinity',
        'statistics_cluster':'official FF++ source pairs' if args.dataset=='ffpp' else args.dataset+' video/sequence IDs; source linkage unavailable, intervals exploratory'}
    write_json(args.output/'environment.json',metadata)
    hook = WGSADiagnostics(model)
    results = {}
    try:
        for method in args.methods:
            # Pair FAA with its no-gradient initialization control; isolate
            # method randomness from which preceding methods were selected.
            offset=2 if method in ('jia-faa-reconstruction','frequency-init-control') else 1 if method=='pgd' else 0
            torch.manual_seed(args.seed+offset)
            started = time.monotonic()
            torch.cuda.reset_peak_memory_stats()
            rows = []
            example_saved = False
            with (args.output/(method+'_per_frame.jsonl')).open('w') as stream:
                for batch in batches:
                    x = batch['image'].cuda(non_blocking=True)
                    y = batch['label'].cuda(non_blocking=True)
                    with torch.no_grad():
                        clean = checked_logits(model,x).sigmoid()
                        before = {k:v.clone() for k,v in hook.current.items()}
                    mask = (y==1)&(clean>=.5)
                    adv = x.detach().clone()
                    hook.enabled = False
                    try:
                        if mask.any() and method!='clean':
                            if method=='fgsm':out=fgsm_jia_reference(model,x[mask],args.epsilon)
                            elif method=='pgd':out=pgd_jia_reference(model,x[mask],args.epsilon,args.steps,args.alpha,restarts=args.pgd_restarts)
                            elif method=='frequency-init-control':out=frequency_initialization_control(model,x[mask],faa)
                            else:out=reconstruct_faa(model,x[mask],faa)
                            adv[mask]=out
                    finally:
                        hook.enabled = True
                    require_finite(adv,'adversarial RGB')
                    if adv.min()<0 or adv.max()>1 or not torch.equal(adv[~mask],x[~mask]):
                        raise AssertionError('RGB/scope violation')
                    with torch.no_grad():
                        attacked = checked_logits(model,adv).sigmoid()
                        after = {k:v.clone() for k,v in hook.current.items()}
                        delta = adv-x
                        linf = delta.abs().flatten(1).amax(1)
                        dct_linf = frequency_norm(delta,args.block,'linf')
                        dct_l2 = frequency_norm(delta,args.block,'l2')
                        if method in ('fgsm','pgd') and (linf>args.epsilon+1e-6).any():
                            raise AssertionError('Pixel budget violation')
                        if method in ('frequency-init-control','jia-faa-reconstruction'):
                            measured=dct_linf if faa.norm=='linf' else dct_l2
                            if (measured>faa.epsilon+max(1e-6,faa.epsilon*1e-5)).any():
                                raise AssertionError('Final frequency budget violation')
                        quality = image_quality(x,adv)
                    if not example_saved and mask.any() and method!='clean':
                        example_index=int(mask.nonzero()[0,0])
                        save_example(args.output/'examples'/method,x[example_index],adv[example_index])
                        example_saved=True
                    for i in range(len(x)):
                        path = Path(batch['path'][i]).resolve().relative_to(args.data_root.resolve()).as_posix()
                        drift = compare_diagnostics({k:v[i:i+1] for k,v in before.items()},
                                                    {k:v[i:i+1] for k,v in after.items()})
                        row = {'record_id_sha256_16':hashlib.sha256(path.encode()).hexdigest()[:16],
                            'label':int(y[i]),'video':batch['video'][i],'manipulation':batch['manipulation'][i],
                            'source_cluster':source_cluster(batch['video'][i],args.dataset,pair_mapping),
                            'attack_applied':bool(mask[i]) and method!='clean',
                            'clean_score':float(clean[i]),'attacked_score':float(attacked[i]),
                            'linf':float(linf[i]),'dct_linf':float(dct_linf[i]),'dct_l2':float(dct_l2[i]),
                            **quality[i],**drift}
                        stream.write(json.dumps(row,allow_nan=False)+'\n')
                        rows.append(row)
                    print(json.dumps({'event':'attack_progress','method':method,'frames':len(rows),'total':len(indices)}),flush=True)
            torch.cuda.synchronize()
            result = evaluation_summary(rows,method)
            result.update(seconds=time.monotonic()-started,peak_allocated_mib=torch.cuda.max_memory_allocated()/1024**2)
            results[method] = result
            write_json(args.output/(method+'_summary.json'),result)
        write_json(args.output/'results.json',{'metadata':metadata,'results':results,'complete':True})
        print('EXP04_V3_COMPLETE '+str(args.output/'results.json'),flush=True)
    finally:
        hook.close()


if __name__=='__main__':
    main()
