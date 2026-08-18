"""Deterministic leakage-aware splitting for CardiBench samples."""
from __future__ import annotations
import random
from collections import defaultdict
from .samples import SampleRecord


def group_key(sample: SampleRecord, preferred: str = "biological_subject") -> str:
    if preferred == "study":
        return sample.study_id
    if preferred == "technical_group" and sample.technical_group:
        return f"technical:{sample.technical_group}"
    if preferred in {"biological_subject", "subject"} and sample.subject_id:
        return f"subject:{sample.study_id}:{sample.subject_id}"
    if sample.biological_group:
        return f"group:{sample.study_id}:{sample.biological_group}"
    return f"sample:{sample.sample_id}"


def make_grouped_split(
    samples: list[SampleRecord],
    *,
    seed: int = 0,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    group_preference: str = "biological_subject",
) -> dict[str, str]:
    """Assign samples to train/validation/test without splitting groups."""
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be within (0,1)")
    if not 0.0 <= validation_fraction < 1.0:
        raise ValueError("validation_fraction must be within [0,1)")
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("train_fraction + validation_fraction must be < 1")

    groups: dict[str, list[SampleRecord]] = defaultdict(list)
    for sample in samples:
        groups[group_key(sample, group_preference)].append(sample)

    group_ids = list(groups)
    random.Random(seed).shuffle(group_ids)
    total = len(group_ids)
    train_n = max(1, round(total * train_fraction))
    val_n = round(total * validation_fraction)
    if train_n + val_n >= total:
        val_n = max(0, total - train_n - 1)

    train_groups = set(group_ids[:train_n])
    val_groups = set(group_ids[train_n:train_n + val_n])
    assignments: dict[str, str] = {}
    for gid, members in groups.items():
        split = "train" if gid in train_groups else "validation" if gid in val_groups else "test"
        for sample in members:
            assignments[sample.sample_id] = split
    return assignments


def split_statistics(assignments: dict[str, str], samples: list[SampleRecord]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for split in ("train", "validation", "test"):
        subset = [s for s in samples if assignments.get(s.sample_id) == split]
        result[split] = {
            "samples": len(subset),
            "subjects": len({s.subject_id for s in subset if s.subject_id}),
            "studies": len({s.study_id for s in subset}),
            "labels": len({s.normalized_label for s in subset if s.normalized_label}),
        }
    return result
