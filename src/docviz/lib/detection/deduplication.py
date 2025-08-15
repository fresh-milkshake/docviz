"""Utilities for post-processing detection results.

This module provides duplicate removal strategies for document layout
detections, including classic Non-Maximum Suppression (NMS) and a simpler
IoU-based deduplication. A convenience `remove_duplicates` function exposes a
single entry point for callers.
"""

from copy import deepcopy

import numpy as np

from docviz.types import DetectionResult


def remove_duplicates_iou(
    detections: list[DetectionResult], iou_threshold: float = 0.5
) -> list[DetectionResult]:
    """
    Remove duplicate or overlapping detections using Intersection over Union (IoU).
    Keeps the detection with the highest confidence for each overlapping group.

    Args:
        detections (list[DetectionResult]): List of detection results.
        iou_threshold (float): IoU threshold for considering detections as duplicates.

    Returns:
        list[DetectionResult]: List of filtered detection results.
    """

    def _compute_iou_vectorized(boxes1: np.ndarray, boxes2: np.ndarray) -> np.ndarray:
        """
        Vectorized IoU computation for multiple box pairs.

        Args:
            boxes1: Array of shape (N, 4) with format [x1, y1, x2, y2]
            boxes2: Array of shape (M, 4) with format [x1, y1, x2, y2]

        Returns:
            IoU matrix of shape (N, M)
        """
        # Expand dimensions for broadcasting
        boxes1 = boxes1[:, np.newaxis, :]  # (N, 1, 4)
        boxes2 = boxes2[np.newaxis, :, :]  # (1, M, 4)

        # Compute intersection coordinates
        xx1 = np.maximum(boxes1[..., 0], boxes2[..., 0])
        yy1 = np.maximum(boxes1[..., 1], boxes2[..., 1])
        xx2 = np.minimum(boxes1[..., 2], boxes2[..., 2])
        yy2 = np.minimum(boxes1[..., 3], boxes2[..., 3])

        # Compute intersection area
        intersection = np.maximum(0.0, xx2 - xx1) * np.maximum(0.0, yy2 - yy1)

        # Compute areas
        area1 = (boxes1[..., 2] - boxes1[..., 0]) * (boxes1[..., 3] - boxes1[..., 1])
        area2 = (boxes2[..., 2] - boxes2[..., 0]) * (boxes2[..., 3] - boxes2[..., 1])

        # Compute union and IoU
        union = area1 + area2 - intersection
        iou = intersection / np.maximum(union, 1e-8)

        return iou

    filtered: list[DetectionResult] = []
    detections_sorted = sorted(detections, key=lambda d: d.confidence, reverse=True)
    used = [False] * len(detections_sorted)

    for i, det in enumerate(detections_sorted):
        if used[i]:
            continue
        filtered.append(det)
        for j in range(i + 1, len(detections_sorted)):
            if used[j]:
                continue
            if det.label == detections_sorted[j].label and (
                _compute_iou_vectorized(np.array(det.bbox), np.array(detections_sorted[j].bbox))
                > iou_threshold
            ):
                used[j] = True

    return filtered


def remove_duplicates_nms(
    detections: list[DetectionResult],
    iou_threshold: float = 0.5,
    soft_nms: bool = False,
    sigma: float = 0.5,
    score_threshold: float = 0.001,
    max_detections: int | None = None,
) -> list[DetectionResult]:
    """
    Advanced Non-Maximum Suppression with optional Soft-NMS support.

    Args:
        detections: List of detection results
        iou_threshold: IoU threshold for NMS (0.0-1.0)
        soft_nms: Enable Soft-NMS instead of hard NMS
        sigma: Gaussian parameter for Soft-NMS
        score_threshold: Minimum confidence threshold
        max_detections: Maximum number of detections to return

    Returns:
        Filtered list of detection results
    """
    if not detections:
        return []

    # Pre-filter by confidence
    detections = [d for d in detections if d.confidence >= score_threshold]
    if not detections:
        return []

    # Group detections by class for efficiency
    class_groups = {}
    for detection in detections:
        if detection.label not in class_groups:
            class_groups[detection.label] = []
        class_groups[detection.label].append(detection)

    filtered_results = []

    # Apply NMS per class
    for class_detections in class_groups.values():
        if soft_nms:
            filtered_results.extend(
                _soft_nms(class_detections, iou_threshold, sigma, score_threshold)
            )
        else:
            filtered_results.extend(_fast_nms(class_detections, iou_threshold))

    # Sort by confidence and limit results
    filtered_results.sort(key=lambda d: d.confidence, reverse=True)

    if max_detections is not None:
        filtered_results = filtered_results[:max_detections]

    return filtered_results


def _fast_nms(detections: list[DetectionResult], iou_threshold: float) -> list[DetectionResult]:
    """Optimized NMS implementation using vectorized operations."""
    if len(detections) <= 1:
        return detections

    # Convert to numpy arrays for vectorized operations
    boxes = np.array([d.bbox for d in detections], dtype=np.float32)
    scores = np.array([d.confidence for d in detections], dtype=np.float32)

    # Sort by confidence
    order = scores.argsort()[::-1]

    # Compute areas once
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)

        if order.size == 1:
            break

        # Compute IoU with remaining boxes
        xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        intersection = w * h

        union = areas[i] + areas[order[1:]] - intersection
        iou = intersection / np.maximum(union, 1e-8)

        # Keep boxes with IoU less than threshold
        inds = np.where(iou <= iou_threshold)[0]
        order = order[inds + 1]

    return [detections[i] for i in keep]


def _soft_nms(
    detections: list[DetectionResult],
    iou_threshold: float,
    sigma: float,
    score_threshold: float,
) -> list[DetectionResult]:
    """
    Soft-NMS implementation that reduces scores instead of removing detections.
    Based on "Improving Object Detection With One Line of Code" (Bodla et al.)
    """
    if len(detections) <= 1:
        return detections

    # Create working copies
    working_detections = deepcopy(detections)

    # Sort by confidence
    working_detections.sort(key=lambda d: d.confidence, reverse=True)

    boxes = np.array([d.bbox for d in working_detections], dtype=np.float32)
    scores = np.array([d.confidence for d in working_detections], dtype=np.float32)
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

    for i in range(len(working_detections)):
        if scores[i] < score_threshold:
            continue

        # Compute IoU with all subsequent boxes
        for j in range(i + 1, len(working_detections)):
            if scores[j] < score_threshold:
                continue

            # Compute IoU
            xx1 = max(boxes[i, 0], boxes[j, 0])
            yy1 = max(boxes[i, 1], boxes[j, 1])
            xx2 = min(boxes[i, 2], boxes[j, 2])
            yy2 = min(boxes[i, 3], boxes[j, 3])

            intersection = max(0.0, xx2 - xx1) * max(0.0, yy2 - yy1)
            union = areas[i] + areas[j] - intersection
            iou = intersection / max(union, 1e-8)

            # Apply soft suppression
            if iou > iou_threshold:
                # Gaussian decay
                scores[j] *= np.exp(-(iou**2) / sigma)
                working_detections[j].confidence = scores[j]

    # Filter by updated scores
    return [d for d in working_detections if d.confidence >= score_threshold]
