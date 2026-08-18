import pytest

from cardi_bench.policies import available_policies, plan_policy_split
from cardi_bench.registry import Sample


def test_policy_catalog_includes_extended_holdouts():
    policies = available_policies()
    assert "species_heldout" in policies
    assert "temporal_heldout" in policies
    assert "cell_context_heldout" in policies
    assert "region_heldout" in policies


def test_species_holdout_uses_preserved_metadata():
    samples = [
        Sample("s1", "a1", "study1", "reference", organism="Mus musculus"),
        Sample("s2", "a2", "study1", "injury", organism="Mus musculus"),
        Sample("s3", "b1", "study2", "reference", organism="Sus scrofa"),
    ]
    result = plan_policy_split(samples, "species_heldout", test_values={"Sus scrofa"})
    assert result["s3"] == "test"
    assert result["s1"] == "train"


def test_temporal_holdout_fails_loudly_on_missing_timepoint():
    samples = [Sample("s1", "a1", "study1", "injury", organism="Mus musculus")]
    with pytest.raises(ValueError, match="timepoint"):
        plan_policy_split(samples, "temporal_heldout", test_values={"day3"})
