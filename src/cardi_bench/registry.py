"""Metadata-first CardiBench registry utilities."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class Sample:
    sample_id: str
    group_id: str
    study_id: str
    label: str
    technical_group: str | None = None


def validate_no_group_leakage(assignments: dict[str, str], samples: Iterable[Sample]) -> list[str]:
    """Return leakage violations for a proposed train/validation/test split."""
    by_group: dict[str, set[str]] = {}
    by_technical: dict[str, set[str]] = {}
    for sample in samples:
        split = assignments.get(sample.sample_id)
        if split is None:
            continue
        by_group.setdefault(sample.group_id, set()).add(split)
        if sample.technical_group:
            by_technical.setdefault(sample.technical_group, set()).add(split)

    violations: list[str] = []
    for group, splits in by_group.items():
        if len(splits) > 1:
            violations.append(f"group leakage: {group} -> {sorted(splits)}")
    for group, splits in by_technical.items():
        if len(splits) > 1:
            violations.append(f"technical-replicate leakage: {group} -> {sorted(splits)}")
    return violations


def summarize_samples(samples: Iterable[Sample]) -> dict[str, int]:
    samples = list(samples)
    return {
        "samples": len(samples),
        "groups": len({s.group_id for s in samples}),
        "studies": len({s.study_id for s in samples}),
        "labels": len({s.label for s in samples}),
    }
