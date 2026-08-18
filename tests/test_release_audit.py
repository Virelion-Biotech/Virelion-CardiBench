from cardi_bench.release import audit_repository_paths


def test_release_audit_accepts_complete_repository():
    paths = [
        "README.md",
        "pyproject.toml",
        "schemas/sample-record.schema.json",
        "schemas/benchmark_definition.schema.json",
        "registry/datasets.yaml",
        "benchmarks/catalog.yaml",
        "tests/test_quality.py",
        ".github/workflows/ci.yml",
    ]
    result = audit_repository_paths(paths)
    assert result.passed
    assert result.errors == ()
    assert result.warnings == ()


def test_release_audit_detects_missing_core_components():
    result = audit_repository_paths(["README.md"])
    assert not result.passed
    assert result.errors
