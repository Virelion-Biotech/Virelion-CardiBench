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
