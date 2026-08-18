from cardi_bench.registry import Sample, validate_no_group_leakage
from cardi_bench.samples import SampleRecord, attach_normalized_label
from cardi_bench.splitting import make_grouped_split, split_statistics


def _samples():
    return [
        SampleRecord("d", "s1", "study-a", "animal-1", "animal-1", "tech-1", "mouse", "heart", "snRNA", "sham"),
        SampleRecord("d", "s2", "study-a", "animal-1", "animal-1", "tech-1", "mouse", "heart", "snRNA", "MI"),
        SampleRecord("d", "s3", "study-a", "animal-2", "animal-2", "tech-2", "mouse", "heart", "snRNA", "MI"),
        SampleRecord("d", "s4", "study-b", "animal-3", "animal-3", "tech-3", "mouse", "heart", "snRNA", "sham"),
        SampleRecord("d", "s5", "study-b", "animal-4", "animal-4", "tech-4", "mouse", "heart", "snRNA", "MI"),
        SampleRecord("d", "s6", "study-c", "animal-5", "animal-5", "tech-5", "mouse", "heart", "snRNA", "sham"),
    ]


def test_condition_normalization():
    record = attach_normalized_label(_samples()[0])
    assert record.normalized_label == "reference"
    assert attach_normalized_label(_samples()[1]).normalized_label == "myocardial_injury"


def test_grouped_split_does_not_leak_subjects():
    samples = [attach_normalized_label(s) for s in _samples()]
    assignments = make_grouped_split(samples, seed=42)
    lightweight = [
        Sample(s.sample_id, s.subject_id or s.study_id, s.study_id, s.normalized_label or "unknown", s.technical_group)
        for s in samples
    ]
    assert validate_no_group_leakage(assignments, lightweight) == []
    stats = split_statistics(assignments, samples)
    assert sum(v["samples"] for v in stats.values()) == len(samples)
