from cardi_bench import Sample, materialize


def _samples():
    return [
        Sample("s1", "a", "study_a", "injury"),
        Sample("s2", "b", "study_a", "reference"),
        Sample("s3", "c", "study_b", "injury"),
        Sample("s4", "d", "study_b", "reference"),
    ]


def test_materialization_is_reproducible():
    rows = _samples()
    first = materialize(rows, benchmark_id="fixture", test_values={"c"}, seed=17)
    second = materialize(rows, benchmark_id="fixture", test_values={"c"}, seed=17)
    assert first.to_json() == second.to_json()
    assert first.assignments["s3"] == "test"
    assert first.sample_count == 4
    assert len(first.metadata_sha256) == 64


def test_materialization_rejects_cross_split_group_leakage():
    rows = [
        Sample("s1", "a", "study_a", "injury"),
        Sample("s2", "a", "study_a", "reference"),
    ]
    first = materialize(rows, benchmark_id="fixture", test_values={"a"})
    assert set(first.assignments.values()) == {"test"}


def test_explicit_subject_partitions_are_exact():
    result = materialize(_samples(), benchmark_id="fixture", test_values={"c"}, validation_values={"b"})
    assert result.assignments == {"s1": "train", "s2": "validation", "s3": "test", "s4": "train"}


def test_metadata_hash_binds_individual_labels():
    from dataclasses import replace
    rows = _samples()
    changed = [replace(rows[0], label=rows[1].label), replace(rows[1], label=rows[0].label), *rows[2:]]
    one = materialize(rows, benchmark_id="fixture", test_values={"c"})
    two = materialize(changed, benchmark_id="fixture", test_values={"c"})
    assert one.label_counts == two.label_counts
    assert one.metadata_sha256 != two.metadata_sha256


def test_rejects_duplicate_ids_and_overlapping_partitions():
    import pytest
    with pytest.raises(ValueError, match="unique"):
        materialize([*_samples(), _samples()[0]], benchmark_id="fixture")
    with pytest.raises(ValueError, match="disjoint"):
        materialize(_samples(), benchmark_id="fixture", test_values={"a"}, validation_values={"a"})
