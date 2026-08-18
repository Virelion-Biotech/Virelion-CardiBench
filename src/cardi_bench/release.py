"""Release-readiness checks for CardiBench."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable

@dataclass(frozen=True)
class AuditResult:
    passed: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def audit_repository_paths(paths: Iterable[str]) -> AuditResult:
    paths = tuple(paths)
    required = {
        "README.md",
        "pyproject.toml",
        "schemas/sample-record.schema.json",
        "schemas/benchmark_definition.schema.json",
    }
    errors = [f"missing required path: {p}" for p in sorted(required - set(paths))]
    if not any(p.startswith("benchmarks/") for p in paths):
        errors.append("no benchmark definitions found")
    if not any(p.startswith("registry/") for p in paths):
        errors.append("no dataset registry found")
    if not any(p.startswith("tests/") for p in paths):
        errors.append("no test suite found")
    warnings: list[str] = []
    if not any("workflow" in PurePosixPath(p).parts for p in paths):
        warnings.append("continuous-integration workflow not detected")
    return AuditResult(not errors, tuple(errors), tuple(warnings))
