from cardi_bench.release import audit_repository_paths


def test_release_audit_accepts_complete_repository():
    paths = [
        "README.md",
        "pyproject.toml",
        "schemas/sample-record.schema.json",
        "schemas/benchmark_definition.schema.json",
        "schemas/split_manifest.schema.json",
        "registry/datasets.yaml",
        "registry/datasets-mi-priority.yaml",
        "benchmarks/catalog.yaml",
        "benchmarks/manifests/mi-vs-reference.v1.json",
        "src/cardi_bench/adapters.py",
        "src/cardi_bench/materialize.py",
        "src/cardi_bench/provenance.py",
        "src/cardi_bench/quality.py",
        "src/cardi_bench/readiness.py",
        "tests/test_quality.py",
        "tests/test_end_to_end_fixture.py",
        ".github/workflows/ci.yml",
        "examples/fixtures/mi_sham_metadata.json",
    ]
    result = audit_repository_paths(paths)
    assert result.passed
    assert result.errors == ()
    assert result.warnings == ()


def test_release_audit_detects_missing_core_components():
    result = audit_repository_paths(["README.md"])
    assert not result.passed
    assert result.errors
