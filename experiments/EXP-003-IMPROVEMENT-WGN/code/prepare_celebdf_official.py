"""Prepare Celeb-DF v2 directly from the authors' official video archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import sys
import time
import zipfile

import common
sys.path.append(str(common.BASE))
import cv2
from facenet_pytorch import MTCNN
import torch

from common import atomic_json
from preprocess_ffpp_official import (
    crop_face,
    detect_boxes,
    fill_missing_boxes,
    sample_frames,
)


DATA = Path('C:/sp/data')
SOURCE = DATA/'official-source'/'Celeb-DF-v2'
ARCHIVE = SOURCE/'Celeb-DF-v2-official.zip'
EXTRACTED = SOURCE/'extracted'
OUTPUT = DATA/'Celeb-DF-v2-official-processed'
MANIFEST = DATA/'Celeb-DF-v2-official-direct.json'
DATASET = 'Celeb-DF-v2-official-direct'
REAL_GROUP = 'CelebDFv2Official_real'
FAKE_GROUP = 'CelebDFv2Official_fake'
OFFICIAL_FILE_ID = '1iLx76wsbi9itnkxSqz9BVBl4ZvnbIazj'


def sha256(path, chunk_size=8*1024*1024):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract(archive, destination):
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive) as handle:
        for member in handle.infolist():
            target = (destination/member.filename).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f'Unsafe archive member: {member.filename}')
        handle.extractall(destination)


def extract_archive(archive, destination):
    if not archive.is_file():
        raise FileNotFoundError(f'Official archive is not ready: {archive}')
    if not zipfile.is_zipfile(archive):
        raise ValueError(f'Official download is not a valid ZIP: {archive}')
    marker = destination/'.archive_complete.json'
    stat = archive.stat()
    if marker.exists():
        completed = json.loads(marker.read_text())
        if (completed.get('bytes') == stat.st_size
                and completed.get('mtime_ns') == stat.st_mtime_ns):
            return completed['sha256']
    digest = sha256(archive)
    safe_extract(archive, destination)
    atomic_json(marker, {'sha256': digest, 'bytes': stat.st_size, 'mtime_ns': stat.st_mtime_ns,
                         'google_drive_file_id': OFFICIAL_FILE_ID})
    return digest


def find_dataset_root(root):
    matches = list(root.rglob('List_of_testing_videos.txt'))
    valid = [path.parent for path in matches if (path.parent/'YouTube-real').is_dir()
             and (path.parent/'Celeb-synthesis').is_dir()]
    if len(valid) != 1:
        raise ValueError(f'Expected one official Celeb-DF v2 root, found {valid}')
    return valid[0]


def read_test_list(root):
    rows = []
    for line in (root/'List_of_testing_videos.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        label, relative = line.split(maxsplit=1)
        if label not in {'0','1'}:
            raise ValueError(f'Invalid official label: {line}')
        path = root.joinpath(*PureWindowsPath(relative).parts)
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append((int(label), relative.replace('\\','/'), path))
    counts = {label: sum(row[0] == label for row in rows) for label in (0,1)}
    if len(rows) != 518 or counts != {0: 340, 1: 178}:
        raise ValueError(f'Expected 518 official test videos (340 fake, 178 real), got {counts}')
    return rows


def relative_windows(path, root):
    return str(PureWindowsPath(*path.relative_to(root).parts))


def prepare(archive, extracted, output, manifest, frames_per_video=32,
            detector_size=512, batch_size=16, smoke=False):
    archive_digest = extract_archive(archive, extracted)
    root = find_dataset_root(extracted)
    rows = read_test_list(root)
    if smoke:
        # Exercise both classes without spending hours before the full stage starts.
        rows = [next(row for row in rows if row[0] == label) for label in (1, 0)]
    test_list_sha = sha256(root/'List_of_testing_videos.txt')
    cv2.setNumThreads(1)
    torch.backends.cudnn.benchmark = True
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA is required for official Celeb-DF face preprocessing')
    mtcnn = MTCNN(image_size=256, margin=0, keep_all=True, select_largest=True,
                  post_process=False, device='cuda')
    payload = {DATASET: {REAL_GROUP: {'train': {}, 'val': {}, 'test': {}},
                         FAKE_GROUP: {'train': {}, 'val': {}, 'test': {}}}}
    missing, center = 0, 0
    started = time.perf_counter()
    for number, (official_label, relative, video_path) in enumerate(rows, start=1):
        # The official list uses 1=real and 0=fake.
        group = REAL_GROUP if official_label == 1 else FAKE_GROUP
        relative_stem = Path(relative).with_suffix('')
        video_key = '__'.join(relative_stem.parts)
        video_output = output/relative_stem
        expected = [video_output/f'{index:06d}.png' for index in range(frames_per_video)]
        if not all(path.is_file() for path in expected):
            video_output.mkdir(parents=True, exist_ok=True)
            frames, source_indices = sample_frames(video_path, frames_per_video)
            boxes, failures = detect_boxes(mtcnn, frames, detector_size, batch_size)
            missing += failures
            center += fill_missing_boxes(boxes, frames)
            if len(frames) != frames_per_video:
                raise RuntimeError(f'Decoded {len(frames)}/{frames_per_video} frames: {video_path}; '
                                   f'indices={source_indices}')
            for output_index, (frame, box) in enumerate(zip(frames, boxes)):
                crop = crop_face(frame, box, 256)
                if not cv2.imwrite(str(expected[output_index]), crop, [cv2.IMWRITE_PNG_COMPRESSION, 3]):
                    raise RuntimeError(f'Failed to write {expected[output_index]}')
        frames = [relative_windows(path, DATA) for path in expected]
        payload[DATASET][group]['test'][video_key] = {'label': group, 'frames': frames,
                                                      'source_video': relative}
        if number % 20 == 0 or number == len(rows):
            elapsed = time.perf_counter()-started
            rate = number/elapsed
            status = {'videos': number, 'total': len(rows), 'videos_per_second': round(rate,3),
                      'eta_minutes': round((len(rows)-number)/rate/60,1),
                      'mtcnn_missing_frames': missing, 'center_fallback_frames': center}
            status_path = manifest.with_suffix('.status.json') if smoke else SOURCE/'preprocess-status.json'
            atomic_json(status_path, status)
            print(json.dumps(status), flush=True)
    temporary = manifest.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    os.replace(temporary, manifest)
    metadata = {'archive_sha256': archive_digest, 'archive_bytes': archive.stat().st_size,
                'test_list_sha256': test_list_sha, 'videos': len(rows),
                'frames': len(rows)*frames_per_video, 'frames_per_video': frames_per_video,
                'detector': 'MTCNN', 'detector_size': detector_size, 'precision': 'fp32',
                'image_size': 256, 'margin': 0, 'select_largest': True,
                'mtcnn_missing_frames': missing, 'center_fallback_frames': center,
                'google_drive_file_id': OFFICIAL_FILE_ID, 'smoke': smoke}
    metadata_path = manifest.with_suffix('.preprocessing.json') if smoke else SOURCE/'preprocessing.json'
    atomic_json(metadata_path, metadata)
    print(f'WROTE_MANIFEST {manifest}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, default=ARCHIVE)
    parser.add_argument('--extracted', type=Path, default=EXTRACTED)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--manifest', type=Path, default=MANIFEST)
    parser.add_argument('--frames-per-video', type=int, default=32)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    prepare(args.archive, args.extracted, args.output, args.manifest, args.frames_per_video,
            smoke=args.smoke)
