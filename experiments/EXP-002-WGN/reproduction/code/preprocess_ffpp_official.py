from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

import cv2
import numpy as np
import torch
from facenet_pytorch import MTCNN


GROUPS = {
    "FF-real": "original_sequences/youtube",
    "FF-DF": "manipulated_sequences/Deepfakes",
    "FF-F2F": "manipulated_sequences/Face2Face",
    "FF-FS": "manipulated_sequences/FaceSwap",
    "FF-NT": "manipulated_sequences/NeuralTextures",
    "FF-FSh": "manipulated_sequences/FaceShifter",
}


@dataclass(frozen=True)
class VideoSpec:
    group: str
    compression: str
    split: str
    path: Path
    count: int


def load_splits(split_root: Path) -> tuple[dict[str, str], dict[str, str]]:
    real_to_split: dict[str, str] = {}
    fake_to_split: dict[str, str] = {}
    for split in ("train", "val", "test"):
        with (split_root / f"{split}.json").open("r", encoding="utf-8") as handle:
            pairs = json.load(handle)
        for first, second in pairs:
            real_to_split[first] = split
            real_to_split[second] = split
            fake_to_split[f"{first}_{second}"] = split
            fake_to_split[f"{second}_{first}"] = split
    if len(real_to_split) != 1000 or len(fake_to_split) != 1000:
        raise RuntimeError(
            f"Unexpected official split sizes: real={len(real_to_split)}, fake={len(fake_to_split)}"
        )
    return real_to_split, fake_to_split


def build_specs(
    input_root: Path,
    split_root: Path,
    compressions: list[str],
    groups: list[str],
    limit_videos: int,
) -> list[VideoSpec]:
    real_to_split, fake_to_split = load_splits(split_root)
    specs: list[VideoSpec] = []
    for compression in compressions:
        for group in groups:
            source = input_root / GROUPS[group] / compression / "videos"
            videos = sorted(source.glob("*.mp4"))
            if len(videos) != 1000:
                raise RuntimeError(f"Expected 1000 videos in {source}, found {len(videos)}")
            if limit_videos > 0:
                videos = videos[:limit_videos]
            split_map = real_to_split if group == "FF-real" else fake_to_split
            count = 40 if group == "FF-real" else 10
            for path in videos:
                try:
                    split = split_map[path.stem]
                except KeyError as error:
                    raise RuntimeError(f"Video {path.name} is absent from official splits") from error
                specs.append(VideoSpec(group, compression, split, path, count))
    return specs


def sample_frames(path: Path, count: int) -> tuple[list[np.ndarray], list[int]]:
    capture = cv2.VideoCapture(str(path))
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        capture.release()
        raise RuntimeError(f"Could not read frame count: {path}")
    indices = np.rint(np.linspace(0, frame_count - 1, count)).astype(int).tolist()
    targets = set(indices)
    frames: list[np.ndarray] = []
    valid_indices: list[int] = []
    index = 0
    while index < frame_count:
        if not capture.grab():
            break
        if index in targets:
            ok, frame = capture.retrieve()
            if ok and frame is not None:
                frames.append(frame)
                valid_indices.append(index)
        index += 1
    capture.release()
    if not frames:
        raise RuntimeError(f"Could not decode sampled frames: {path}")
    return frames, valid_indices


def letterbox_rgb(frame_bgr: np.ndarray, size: int) -> tuple[np.ndarray, float, int, int]:
    height, width = frame_bgr.shape[:2]
    scale = min(size / width, size / height)
    resized_width = max(1, round(width * scale))
    resized_height = max(1, round(height * scale))
    resized = cv2.resize(frame_bgr, (resized_width, resized_height), interpolation=cv2.INTER_AREA)
    pad_x = (size - resized_width) // 2
    pad_y = (size - resized_height) // 2
    canvas = np.full((size, size, 3), 127, dtype=np.uint8)
    canvas[pad_y : pad_y + resized_height, pad_x : pad_x + resized_width] = resized
    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB), scale, pad_x, pad_y


def detect_boxes(
    mtcnn: MTCNN,
    frames: list[np.ndarray],
    detector_size: int,
    batch_size: int,
) -> tuple[list[np.ndarray | None], int]:
    mapped_boxes: list[np.ndarray | None] = [None] * len(frames)
    detection_failures = 0
    for start in range(0, len(frames), batch_size):
        chunk = frames[start : start + batch_size]
        prepared = [letterbox_rgb(frame, detector_size) for frame in chunk]
        images = np.stack([item[0] for item in prepared])
        boxes, _ = mtcnn.detect(images)
        for offset, (candidates, prepared_item) in enumerate(zip(boxes, prepared)):
            index = start + offset
            if candidates is None or len(candidates) == 0:
                detection_failures += 1
                continue
            scale, pad_x, pad_y = prepared_item[1:]
            box = np.asarray(candidates[0], dtype=np.float32)
            box[[0, 2]] = (box[[0, 2]] - pad_x) / scale
            box[[1, 3]] = (box[[1, 3]] - pad_y) / scale
            mapped_boxes[index] = box
    return mapped_boxes, detection_failures


def fill_missing_boxes(boxes: list[np.ndarray | None], frames: list[np.ndarray]) -> int:
    valid = [index for index, box in enumerate(boxes) if box is not None]
    if valid:
        for index, box in enumerate(boxes):
            if box is None:
                nearest = min(valid, key=lambda candidate: abs(candidate - index))
                boxes[index] = boxes[nearest].copy()
        return 0
    for index, frame in enumerate(frames):
        height, width = frame.shape[:2]
        side = min(height, width)
        left = (width - side) / 2
        top = (height - side) / 2
        boxes[index] = np.asarray([left, top, left + side, top + side], dtype=np.float32)
    return len(frames)


def crop_face(frame: np.ndarray, box: np.ndarray, image_size: int) -> np.ndarray:
    height, width = frame.shape[:2]
    left, top, right, bottom = [float(value) for value in box]
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    side = max(right - left, bottom - top)
    left = max(0, int(round(center_x - side / 2)))
    top = max(0, int(round(center_y - side / 2)))
    right = min(width, int(round(center_x + side / 2)))
    bottom = min(height, int(round(center_y + side / 2)))
    if right <= left or bottom <= top:
        raise RuntimeError("Invalid MTCNN crop box")
    crop = frame[top:bottom, left:right]
    return cv2.resize(crop, (image_size, image_size), interpolation=cv2.INTER_AREA)


def relative_windows(path: Path, root: Path) -> str:
    return str(PureWindowsPath(*path.relative_to(root).parts))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", default="C:/sp1/data/FaceForensics++-official")
    parser.add_argument("--output-root", default="C:/sp1/data/FaceForensics++-official-processed")
    parser.add_argument("--data-root", default="C:/sp1/data")
    parser.add_argument("--split-root", default="C:/sp1/WGN/splits")
    parser.add_argument("--manifest", default="C:/sp1/data/FaceForensics++-official.json")
    parser.add_argument("--compressions", nargs="+", default=["c23", "c40"])
    parser.add_argument("--groups", nargs="+", default=list(GROUPS))
    parser.add_argument("--image-size", type=int, default=256)
    parser.add_argument("--detector-size", type=int, default=640)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--precision", choices=("fp32", "fp16"), default="fp32")
    parser.add_argument("--limit-videos", type=int, default=0)
    args = parser.parse_args()

    cv2.setNumThreads(1)
    torch.backends.cudnn.benchmark = True
    input_root = Path(args.input_root).resolve()
    output_root = Path(args.output_root).resolve()
    data_root = Path(args.data_root).resolve()
    split_root = Path(args.split_root).resolve()
    specs = build_specs(
        input_root,
        split_root,
        list(args.compressions),
        list(args.groups),
        args.limit_videos,
    )
    mtcnn = MTCNN(
        image_size=args.image_size,
        margin=0,
        keep_all=True,
        select_largest=True,
        post_process=False,
        device="cuda",
    )
    if args.precision == "fp16":
        mtcnn.half()

    manifest = {
        "FaceForensics++": {
            group: {
                split: {compression: {} for compression in args.compressions}
                for split in ("train", "val", "test")
            }
            for group in args.groups
        }
    }
    total_detection_failures = 0
    total_center_fallbacks = 0
    started = time.perf_counter()
    for number, spec in enumerate(specs, start=1):
        video_output = output_root / spec.group / spec.compression / spec.path.stem
        expected = [video_output / f"{index:06d}.png" for index in range(spec.count)]
        if not all(path.is_file() for path in expected):
            video_output.mkdir(parents=True, exist_ok=True)
            frames, source_indices = sample_frames(spec.path, spec.count)
            boxes, failures = detect_boxes(
                mtcnn,
                frames,
                args.detector_size,
                args.batch_size,
            )
            total_detection_failures += failures
            total_center_fallbacks += fill_missing_boxes(boxes, frames)
            for output_index, (frame, box) in enumerate(zip(frames, boxes)):
                crop = crop_face(frame, box, args.image_size)
                output_path = video_output / f"{output_index:06d}.png"
                if not cv2.imwrite(str(output_path), crop, [cv2.IMWRITE_PNG_COMPRESSION, 3]):
                    raise RuntimeError(f"Failed to write {output_path}")
            if len(frames) < spec.count:
                raise RuntimeError(
                    f"Decoded only {len(frames)}/{spec.count} frames from {spec.path}; "
                    f"source indices={source_indices}"
                )

        frame_paths = [relative_windows(path, data_root) for path in expected]
        manifest["FaceForensics++"][spec.group][spec.split][spec.compression][spec.path.stem] = {
            "label": spec.group,
            "frames": frame_paths,
        }
        if number % 20 == 0 or number == len(specs):
            elapsed = time.perf_counter() - started
            rate = number / elapsed
            remaining = (len(specs) - number) / rate if rate else 0
            print(
                json.dumps(
                    {
                        "videos": number,
                        "total": len(specs),
                        "videos_per_second": round(rate, 3),
                        "eta_minutes": round(remaining / 60, 1),
                        "mtcnn_missing_frames": total_detection_failures,
                        "center_fallback_frames": total_center_fallbacks,
                    }
                ),
                flush=True,
            )

    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
    print(f"WROTE_MANIFEST {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

