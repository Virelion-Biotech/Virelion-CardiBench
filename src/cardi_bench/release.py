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
    available = set(paths)
    required = {
        "README.md",
        "pyproject.toml",
        "schemas/sample-record.schema.json",
        "schemas/benchmark_definition.schema.json",
        "schemas/split_manifest.schema.json",
        "src/cardi_bench/adapters.py",
        "src/cardi_bench/materialize.py",
        "src/cardi_bench/provenance.py",
        "src/cardi_bench/quality.py",
        "src/cardi_bench/readiness.py",
        "tests/test_end_to_end_fixture.py",
    }
    errors = [f"missing required path: {p}" for p in sorted(required - available)]
    if not any(p.startswith("benchmarks/") for p in paths):
        errors.append("no benchmark definitions found")
    if not any(p.startswith("registry/") for p in paths):
        errors.append("no dataset registry found")
    if not any(p.startswith("tests/") for p in paths):
        errors.append("no test suite found")
    warnings: list[str] = []
    if not any("workflow" in PurePosixPath(p).parts for p in paths):
        warnings.append("continuous-integration workflow not detected")
    if not any(p.startswith("examples/fixtures/") for p in paths):
        warnings.append("no end-to-end fixture metadata found")
    return AuditResult(not errors, tuple(errors), tuple(warnings))
