"""Dataset and cohort quality gates for CardiBench."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from .samples import SampleRecord
from .splitting import split_statistics
from .registry import validate_no_group_leakage, Sample

@dataclass(frozen=True)
class QualityReport:
    passed: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    statistics: dict


def assess_dataset(samples: list[SampleRecord], assignments: dict[str, str] | None = None) -> QualityReport:
    errors: list[str] = []
    warnings: list[str] = []
    if not samples:
        return QualityReport(False, ("dataset contains no samples",), (), {})
    ids = [s.sample_id for s in samples]
    duplicate_ids = [k for k, v in Counter(ids).items() if v > 1]
    if duplicate_ids:
        errors.append(f"duplicate sample IDs: {duplicate_ids[:10]}")
    unnormalized = [s.sample_id for s in samples if not s.normalized_label]
    if unnormalized:
        errors.append(f"unresolved phenotype labels: {len(unnormalized)} samples")
    missing_groups = [s.sample_id for s in samples if not s.subject_id and not s.biological_group]
    if missing_groups:
        warnings.append(f"missing biological grouping metadata: {len(missing_groups)} samples")
    labels = Counter(s.normalized_label for s in samples)
    if len(labels) < 2:
        errors.append("cohort has fewer than two normalized labels")
    stats = {"samples": len(samples), "labels": dict(labels), "studies": len({s.study_id for s in samples})}
    if assignments:
        stats["splits"] = split_statistics(assignments, samples)
        bridge = [Sample(s.sample_id, s.subject_id or s.biological_group or s.sample_id, s.study_id, s.normalized_label or "unknown", s.technical_group) for s in samples]
        leakage = validate_no_group_leakage(assignments, bridge)
        if leakage:
            errors.extend(leakage)
    return QualityReport(not errors, tuple(errors), tuple(warnings), stats)
