"""Backward-compatible aliases for the canonical deterministic splitter."""
from __future__ import annotations

from .splits import make_group_split, split_summary
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
    """Compatibility wrapper around the canonical group splitter."""
    remaining = max(0.0, 1.0 - train_fraction - validation_fraction)
    if remaining <= 0.0:
        raise ValueError("train_fraction + validation_fraction must be < 1")
    group_by = "study_id" if group_preference == "study" else "group_id"
    return make_group_split([_to_sample(sample) for sample in samples], seed=seed,
                            train_fraction=train_fraction, validation_fraction=validation_fraction,
                            test_fraction=remaining, group_by=group_by)


def split_statistics(assignments: dict[str, str], samples: list[SampleRecord]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for split in ("train", "validation", "test"):
        subset = [s for s in samples if assignments.get(s.sample_id) == split]
        result[split] = {
            "samples": len(subset),
            "subjects": len({s.subject_id for s in subset if s.subject_id}),
            "studies": len({s.study_id for s in subset}),
            "labels": len({getattr(s, "normalized_label", None) for s in subset if getattr(s, "normalized_label", None)}),
        }
    return result


def _to_sample(sample: SampleRecord):
    from .registry import Sample
    return Sample(
        sample_id=sample.sample_id,
        group_id=getattr(sample, "subject_id", None) or getattr(sample, "biological_group", None) or sample.sample_id,
        study_id=sample.study_id,
        label=getattr(sample, "normalized_label", None) or getattr(sample, "raw_condition", None) or "unknown",
        technical_group=getattr(sample, "technical_group", None),
    )
