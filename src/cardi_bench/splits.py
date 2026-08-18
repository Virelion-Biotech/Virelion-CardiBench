"""Deterministic group-aware benchmark splitting."""
from __future__ import annotations
from collections import defaultdict
import hashlib
from .registry import Sample


def _bucket(key: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def make_group_split(
    samples: list[Sample],
    *,
    seed: int = 0,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    test_fraction: float = 0.15,
    group_by: str = "group_id",
) -> dict[str, str]:
    """Assign complete biological groups to train/validation/test.

    The assignment is deterministic for a seed and never splits a biological
    group. For study-held-out benchmarks pass group_by='study_id'.
    """
    total = train_fraction + validation_fraction + test_fraction
    if abs(total - 1.0) > 1e-8:
        raise ValueError("split fractions must sum to 1")
    if not samples:
        return {}
    if group_by not in {"group_id", "study_id"}:
        raise ValueError("group_by must be 'group_id' or 'study_id'")

    groups: dict[str, list[Sample]] = defaultdict(list)
    for sample in samples:
        groups[getattr(sample, group_by)].append(sample)

    ordered = sorted(groups, key=lambda key: _bucket(key, seed))
    assignments: dict[str, str] = {}
    for key in ordered:
        p = _bucket(f"split:{key}", seed)
        if p < train_fraction:
            split = "train"
        elif p < train_fraction + validation_fraction:
            split = "validation"
        else:
            split = "test"
        for sample in groups[key]:
            assignments[sample.sample_id] = split

    return assignments


def split_summary(assignments: dict[str, str]) -> dict[str, int]:
    summary = {"train": 0, "validation": 0, "test": 0}
    for split in assignments.values():
        if split not in summary:
            raise ValueError(f"unknown split: {split}")
        summary[split] += 1
    return summary
