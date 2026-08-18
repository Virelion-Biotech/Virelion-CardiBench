"""Turn normalized sample records into reproducible benchmark instances."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Iterable

from .registry import Sample
from .splits import plan_group_split
from .policies import plan_policy_split
from .benchmark import assert_benchmark_safe, label_counts


@dataclass(frozen=True)
class MaterializedBenchmark:
    benchmark_id: str
    version: str
    policy: str
    seed: int
    assignments: dict[str, str]
    label_counts: dict[str, dict[str, int]]
    sample_count: int
    group_count: int
    metadata_sha256: str

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def materialize(
    samples: Iterable[Sample],
    *,
    benchmark_id: str,
    version: str = "1.0",
    policy: str = "subject_heldout",
    test_values: set[str] | None = None,
    validation_values: set[str] | None = None,
    seed: int = 0,
) -> MaterializedBenchmark:
    """Create a locked, reproducible split manifest from normalized samples."""
    rows = list(samples)
    if not rows:
        raise ValueError("cannot materialize an empty benchmark")
    if seed < 0:
        raise ValueError("seed must be non-negative")
    test_values = test_values or set()
    validation_values = validation_values or set()

    if policy == "subject_heldout":
        assignments = plan_group_split(
            rows,
            test_groups=test_values,
            validation_groups=validation_values,
            seed=seed,
        ).assignments
    else:
        assignments = plan_policy_split(
            rows,
            policy,
            test_values=test_values,
            validation_values=validation_values,
        )

    assert_benchmark_safe(rows, assignments)
    counts = label_counts(rows, assignments)
    canonical = {
        "benchmark_id": benchmark_id,
        "version": version,
        "policy": policy,
        "assignments": dict(sorted(assignments.items())),
        "labels": counts,
        "seed": seed,
    }
    digest = sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return MaterializedBenchmark(
        benchmark_id=benchmark_id,
        version=version,
        policy=policy,
        seed=seed,
        assignments=assignments,
        label_counts=counts,
        sample_count=len(rows),
        group_count=len({r.group_id for r in rows}),
        metadata_sha256=digest,
    )
