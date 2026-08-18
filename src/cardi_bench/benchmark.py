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


def validate_policy_integrity(samples: Iterable[Sample], assignments: dict[str, str], policy: str) -> list[str]:
    """Return violations for the dimension that defines a declared split policy."""
    key_by_policy = {
        "study_heldout": "study_id",
        "species_heldout": "organism",
        "temporal_heldout": "timepoint",
        "cell_context_heldout": "cell_context",
        "region_heldout": "region",
    }
    key = key_by_policy.get(policy)
    if key is None:
        return []
    by_value: dict[object, set[str]] = defaultdict(set)
    for sample in samples:
        split = assignments.get(sample.sample_id)
        if split is None:
            continue
        value = getattr(sample, key)
        if value is None or value == "":
            return [f"policy metadata missing: {key} for {sample.sample_id}"]
        by_value[value].add(split)
    return [
        f"policy leakage: {key}={value!r} -> {sorted(splits)}"
        for value, splits in by_value.items()
        if len(splits) > 1
    ]


def assert_benchmark_safe(samples: Iterable[Sample], assignments: dict[str, str], policy: str | None = None) -> None:
    samples = list(samples)
    violations = validate_no_group_leakage(assignments, samples)
    if policy:
        violations.extend(validate_policy_integrity(samples, assignments, policy))
    if violations:
        raise ValueError("Benchmark leakage detected: " + "; ".join(violations))
