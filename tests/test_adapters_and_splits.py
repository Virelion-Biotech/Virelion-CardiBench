from cardi_bench import Sample, adapt_geo_samples, make_group_split, validate_no_group_leakage


def test_geo_adapter_normalizes_mi_and_sham():
    result = adapt_geo_samples([
        {"sample_id": "S1", "title": "MI day 3", "animal_id": "A1"},
        {"sample_id": "S2", "title": "sham day 3", "animal_id": "A2"},
    ], study_id="GSE-test")
    assert [s.label for s in result.samples] == ["myocardial_injury", "reference"]
    assert not result.rejected


def test_adapter_rejects_ambiguous_metadata():
    result = adapt_geo_samples([
        {"sample_id": "S1", "title": "MI sham", "animal_id": "A1"},
    ], study_id="GSE-test")
    assert result.rejected
    assert not result.samples


def test_group_split_prevents_group_leakage():
    samples = [
        Sample("S1", "A1", "study-a", "myocardial_injury", "T1"),
        Sample("S2", "A1", "study-a", "myocardial_injury", "T1"),
        Sample("S3", "A2", "study-a", "reference", "T2"),
        Sample("S4", "A3", "study-b", "reference", "T3"),
    ]
    assignments = make_group_split(samples, seed=3, group_by="group_id")
    assert not validate_no_group_leakage(assignments, samples)
