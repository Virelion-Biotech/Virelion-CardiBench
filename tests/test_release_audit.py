from cardi_bench.release import audit_repository_paths


def test_release_audit_accepts_complete_repository():
    paths = [
        "README.md",
        "pyproject.toml",
        "schemas/sample-record.schema.json",
        "schemas/benchmark_definition.schema.json",
        "schemas/benchmark_result.schema.json",
        "schemas/split_manifest.schema.json",
        "registry/datasets.yaml",
        "registry/datasets-mi-priority.yaml",
        "benchmarks/catalog.yaml",
        "benchmarks/manifests/mi-vs-reference.v1.json",
        "src/cardi_bench/admission.py",
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
        "scripts/generate_reference_result.py",
        ".github/workflows/reference-evaluation.yml",
        "tests/test_quality.py",
        "tests/test_materialize.py",
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
