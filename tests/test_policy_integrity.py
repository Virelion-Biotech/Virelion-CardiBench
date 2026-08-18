import pytest

from cardi_bench.benchmark import assert_benchmark_safe
from cardi_bench.materialize import materialize
from cardi_bench.registry import Sample


def test_species_policy_detects_cross_split_species_leakage():
    samples = [
        Sample("a", "a", "study1", "reference", organism="Mus musculus"),
        Sample("b", "b", "study2", "injury", organism="Mus musculus"),
    ]
    with pytest.raises(ValueError, match="policy leakage"):
        assert_benchmark_safe(samples, {"a": "train", "b": "test"}, policy="species_heldout")


def test_temporal_policy_is_enforced_by_materializer():
    samples = [
        Sample("a", "a", "study1", "reference", timepoint="day1"),
        Sample("b", "b", "study1", "injury", timepoint="day3"),
    ]
    benchmark = materialize(
        samples,
        benchmark_id="temporal-test",
        policy="temporal_heldout",
        test_values={"day3"},
    )
    assert benchmark.assignments["b"] == "test"
    assert benchmark.seed == 0
