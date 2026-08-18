"""Benchmark planning and integrity checks."""
from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from typing import Iterable

from .registry import Sample, validate_no_group_leakage

@dataclass(frozen=True)
class SplitPlan:
    assignments: dict[str, str]
    policy: str
    warnings: tuple[str, ...] = ()


def plan_group_split(samples: Iterable[Sample], *, test_groups: set[str], validation_groups: set[str] | None = None) -> SplitPlan:
    """Assign complete biological groups to partitions; never split a group."""
    validation_groups = validation_groups or set()
    assignments: dict[str, str] = {}
    warnings: list[str] = []
    for sample in samples:
        if sample.group_id in test_groups:
            split = "test"
        elif sample.group_id in validation_groups:
            split = "validation"
        else:
            split = "train"
        assignments[sample.sample_id] = split
    violations = validate_no_group_leakage(assignments, samples)
    if violations:
        warnings.extend(violations)
    return SplitPlan(assignments, "group", tuple(warnings))


def label_counts(samples: Iterable[Sample], assignments: dict[str, str]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for sample in samples:
        split = assignments.get(sample.sample_id)
        if split:
            counts[split][sample.label] += 1
    return {split: dict(labels) for split, labels in counts.items()}


def assert_benchmark_safe(samples: Iterable[Sample], assignments: dict[str, str]) -> None:
    samples = list(samples)
    violations = validate_no_group_leakage(assignments, samples)
    if violations:
        raise ValueError("Benchmark leakage detected: " + "; ".join(violations))
