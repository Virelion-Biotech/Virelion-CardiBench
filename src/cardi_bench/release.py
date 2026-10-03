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
    available = set(paths)
    required = {
        "README.md",
        "pyproject.toml",
        "schemas/sample-record.schema.json",
        "schemas/benchmark_definition.schema.json",
        "schemas/benchmark_result.schema.json",
        "schemas/split_manifest.schema.json",
        "src/cardi_bench/adapters.py",
        "src/cardi_bench/analytics.py",
        "src/cardi_bench/api.py",
        "src/cardi_bench/dashboard.py",
        "src/cardi_bench/discovery.py",
        "src/cardi_bench/evidence.py",
        "src/cardi_bench/identity.py",
        "src/cardi_bench/intelligence_store.py",
        "src/cardi_bench/materialize.py",
        "src/cardi_bench/policies.py",
        "src/cardi_bench/provenance.py",
        "src/cardi_bench/quality.py",
        "src/cardi_bench/readiness.py",
        "src/cardi_bench/results.py",
        "src/cardi_bench/result_history.py",
        "src/cardi_bench/release_bundle.py",
        "src/cardi_bench/search.py",
        "tests/test_end_to_end_fixture.py",
        "tests/test_materialize.py",
    }
    errors = [f"missing required path: {p}" for p in sorted(required - available)]
    if not any(p.startswith("benchmarks/") for p in available):
        errors.append("no benchmark definitions found")
    if not any(p.startswith("registry/") for p in available):
        errors.append("no dataset registry found")
    if not any(p.startswith("tests/") for p in available):
        errors.append("no test suite found")
    warnings: list[str] = []
    if not any(".github/workflows/" in p for p in available):
        warnings.append("continuous-integration workflow not detected")
    if not any(p.startswith("examples/fixtures/") for p in available):
        warnings.append("no end-to-end fixture metadata found")
    return AuditResult(not errors, tuple(errors), tuple(warnings))
