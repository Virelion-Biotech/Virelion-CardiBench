"""Standardized result records consumed by CardiEval and downstream models."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Mapping


@dataclass(frozen=True)
class BenchmarkResult:
    benchmark_id: str
    model_id: str
    model_version: str
    split: str
    metrics: Mapping[str, float]
    sample_count: int
    provenance_sha256: str
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def validate(self) -> None:
        if not self.benchmark_id or not self.model_id or not self.model_version:
            raise ValueError("benchmark and model identifiers are required")
        if self.split not in {"validation", "test"}:
            raise ValueError("results must be reported on validation or test splits")
        if self.sample_count < 1:
            raise ValueError("sample_count must be positive")
        if not self.provenance_sha256 or len(self.provenance_sha256) != 64:
            raise ValueError("provenance_sha256 must be a 64-character digest")
        for name, value in self.metrics.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f"metric {name} is not numeric")
