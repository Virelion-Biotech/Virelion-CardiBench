from cardi_bench.quality import assess_dataset
from cardi_bench.samples import SampleRecord
from cardi_bench.splitting import make_grouped_split


def _samples():
    return [
        SampleRecord("d", "s1", "study-a", "a1", "a1", "lib1", "Mus musculus", "heart", "snRNA-seq", "sham", "reference"),
        SampleRecord("d", "s2", "study-a", "a2", "a2", "lib2", "Mus musculus", "heart", "snRNA-seq", "MI", "myocardial_injury"),
        SampleRecord("d", "s3", "study-b", "b1", "b1", "lib3", "Mus musculus", "heart", "snRNA-seq", "sham", "reference"),
        SampleRecord("d", "s4", "study-b", "b2", "b2", "lib4", "Mus musculus", "heart", "snRNA-seq", "MI", "myocardial_injury"),
    ]


def test_quality_passes_for_two_label_cohort():
    samples = _samples()
    assignments = make_grouped_split(samples, seed=4, train_fraction=0.5, validation_fraction=0.25)
    report = assess_dataset(samples, assignments)
    assert report.passed
    assert report.statistics["samples"] == 4


def test_quality_catches_unresolved_labels():
    samples = _samples()
    samples[0] = SampleRecord("d", "s1", "study-a", "a1", "a1", "lib1", "Mus musculus", "heart", "snRNA-seq", "mystery", None)
    report = assess_dataset(samples)
    assert not report.passed
    assert any("unresolved phenotype labels" in error for error in report.errors)
