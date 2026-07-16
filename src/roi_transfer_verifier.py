#!/usr/bin/env python3
"""Measure item occupancy in a fixed delivery-tray ROI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def parse_roi(value: str) -> tuple[int, int, int, int]:
    parts = tuple(int(part) for part in value.split(","))
    if len(parts) != 4 or min(parts) < 0 or parts[2] <= 0 or parts[3] <= 0:
        raise argparse.ArgumentTypeError("ROI must be x,y,width,height with positive size")
    return parts


def parse_polygon(value: str) -> np.ndarray:
    try:
        points = [[int(axis) for axis in point.split(",")] for point in value.split(";")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("polygon must be x,y;x,y;...") from exc
    if len(points) < 3 or any(len(point) != 2 for point in points):
        raise argparse.ArgumentTypeError("polygon must contain at least three x,y points")
    return np.asarray(points, dtype=np.int32)


def crop_image(path: Path, roi: tuple[int, int, int, int]) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Unable to read image: {path}")
    x, y, width, height = roi
    crop = image[y : y + height, x : x + width]
    if crop.shape[:2] != (height, width):
        raise ValueError(f"ROI {roi} exceeds image size {image.shape[1]}x{image.shape[0]}")
    return crop


def measure_occupancy(
    empty_reference: np.ndarray,
    current: np.ndarray,
    polygon: np.ndarray,
    pixel_threshold: int = 28,
    minimum_component_area: int = 300,
) -> tuple[float, np.ndarray, list[int]]:
    if empty_reference.shape != current.shape:
        raise ValueError("reference and current images must have identical dimensions")

    mask = np.zeros(empty_reference.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    reference_blur = cv2.GaussianBlur(empty_reference, (7, 7), 0)
    current_blur = cv2.GaussianBlur(current, (7, 7), 0)
    difference = cv2.cvtColor(cv2.absdiff(reference_blur, current_blur), cv2.COLOR_BGR2GRAY)
    changed = cv2.threshold(difference, pixel_threshold, 255, cv2.THRESH_BINARY)[1]
    changed = cv2.bitwise_and(changed, mask)
    changed = cv2.morphologyEx(changed, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    changed = cv2.morphologyEx(changed, cv2.MORPH_CLOSE, np.ones((13, 13), np.uint8))

    component_count, _, stats, _ = cv2.connectedComponentsWithStats(changed)
    component_areas = sorted(
        [
            int(stats[index, cv2.CC_STAT_AREA])
            for index in range(1, component_count)
            if stats[index, cv2.CC_STAT_AREA] >= minimum_component_area
        ],
        reverse=True,
    )
    filtered = np.zeros_like(changed)
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(changed)
    for index in range(1, component_count):
        if stats[index, cv2.CC_STAT_AREA] >= minimum_component_area:
            filtered[labels == index] = 255

    mask_area = cv2.countNonZero(mask)
    occupancy = cv2.countNonZero(filtered) / mask_area if mask_area else 0.0
    return occupancy, filtered, component_areas


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare delivery-tray images against an empty fixed-camera reference."
    )
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--images", type=Path, nargs="+", required=True)
    parser.add_argument("--roi", type=parse_roi, required=True, help="x,y,width,height")
    parser.add_argument(
        "--polygon",
        type=parse_polygon,
        required=True,
        help="Tray polygon relative to the ROI: x,y;x,y;...",
    )
    parser.add_argument("--pixel-threshold", type=int, default=28)
    parser.add_argument("--minimum-component-area", type=int, default=300)
    parser.add_argument("--overlay", type=Path)
    args = parser.parse_args()

    reference = crop_image(args.reference, args.roi)
    measurements = []
    overlays = []
    for path in args.images:
        current = crop_image(path, args.roi)
        occupancy, changed, areas = measure_occupancy(
            reference,
            current,
            args.polygon,
            args.pixel_threshold,
            args.minimum_component_area,
        )
        measurements.append(
            {
                "image": str(path),
                "destination_occupancy": round(occupancy, 6),
                "component_areas": areas,
            }
        )
        overlay = current.copy()
        overlay[changed > 0] = (
            0.35 * overlay[changed > 0] + 0.65 * np.asarray([0, 0, 255])
        ).astype(np.uint8)
        cv2.polylines(overlay, [args.polygon], True, (0, 255, 255), 3)
        overlays.append(overlay)

    if args.overlay:
        args.overlay.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(args.overlay), np.hstack(overlays))
    print(json.dumps({"measurements": measurements}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
