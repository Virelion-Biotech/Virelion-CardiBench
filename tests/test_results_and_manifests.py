import json
from pathlib import Path

from cardi_bench import BenchmarkResult, validate_manifest


def test_benchmark_result_requires_test_or_validation_split():
    result = BenchmarkResult(
        benchmark_id="fixture",
        model_id="model-a",
        model_version="1",
        split="test",
        metrics={"auroc": 0.91},
        sample_count=4,
        provenance_sha256="a" * 64,
    )
    result.validate()


def test_benchmark_result_rejects_training_results():
    result = BenchmarkResult(
        benchmark_id="fixture",
        model_id="model-a",
        model_version="1",
        split="train",
        metrics={"auroc": 0.91},
        sample_count=4,
        provenance_sha256="a" * 64,
    )
    try:
        result.validate()
    except ValueError as exc:
        assert "validation or test" in str(exc)
    else:
        raise AssertionError("training results must not be accepted")


def test_json_benchmark_manifests_are_structurally_complete():
    for path in sorted(Path("benchmarks/manifests").glob("*.json")):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_manifest(manifest)
        assert not errors, f"{path}: {errors}"
