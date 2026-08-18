"""Reusable split policies for cardiac benchmarks."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .registry import Sample

@dataclass(frozen=True)
class Policy:
    name: str
    primary_key: str
    description: str
    requires_value: bool = True

POLICIES = {
    "subject_heldout": Policy("subject_heldout", "group_id", "No biological subject/group appears in more than one split."),
    "study_heldout": Policy("study_heldout", "study_id", "Entire studies are held out from test."),
    "species_heldout": Policy("species_heldout", "organism", "Entire species are held out from test."),
    "temporal_heldout": Policy("temporal_heldout", "timepoint", "Selected timepoints are held out from test when comparable groups exist."),
    "cell_context_heldout": Policy("cell_context_heldout", "cell_context", "Selected cardiac cell contexts are held out from test when comparable groups exist."),
    "region_heldout": Policy("region_heldout", "region", "Selected anatomical regions are held out from test when comparable groups exist."),
}

def available_policies() -> tuple[str, ...]:
    return tuple(POLICIES)

def plan_policy_split(
    samples: Iterable[Sample],
    policy: str,
    *,
    test_values: set[str],
    validation_values: set[str] | None = None,
) -> dict[str, str]:
    """Apply a declared benchmark policy without silently splitting missing metadata."""
    if policy not in POLICIES:
        raise ValueError(f"Unknown split policy: {policy}")
    validation_values = validation_values or set()
    assignments: dict[str, str] = {}
    missing: list[str] = []
    for sample in samples:
        value = getattr(sample, POLICIES[policy].primary_key)
        if value is None or value == "":
            missing.append(sample.sample_id)
            continue
        if value in test_values:
            split = "test"
        elif value in validation_values:
            split = "validation"
        else:
            split = "train"
        assignments[sample.sample_id] = split
    if missing:
        raise ValueError(
            f"policy {policy} requires {POLICIES[policy].primary_key}; missing for {len(missing)} samples"
        )
    return assignments
