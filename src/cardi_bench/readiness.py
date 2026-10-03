"""Readiness gates for promoting CardiBench metadata into benchmarks."""
from __future__ import annotations
from dataclasses import dataclass
from .quality import QualityReport, assess_dataset
from .manifest import validate_manifest

@dataclass(frozen=True)
class ReadinessReport:
    ready: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    score: float


def assess_readiness(samples, *, manifest: dict | None = None) -> ReadinessReport:
    blockers: list[str] = []
    warnings: list[str] = []
    quality: QualityReport = assess_dataset(list(samples))
    blockers.extend(quality.errors)
    warnings.extend(quality.warnings)
    if manifest is not None:
        blockers.extend(validate_manifest(manifest))
    checks = 5
    failed = min(checks, len(blockers))
    score = max(0.0, 1.0 - failed / checks)
    if not samples:
        score = 0.0
    return ReadinessReport(not blockers, tuple(blockers), tuple(warnings), score)
