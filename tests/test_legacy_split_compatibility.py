from cardi_bench.samples import SampleRecord
from cardi_bench.splitting import make_grouped_split


def test_legacy_split_wrapper_matches_group_constraints():
    samples = [
        SampleRecord("d", "s1", "study", "a", "a", None, "mouse", "heart", "snRNA", "MI", "myocardial_injury"),
        SampleRecord("d", "s2", "study", "b", "b", None, "mouse", "heart", "snRNA", "sham", "reference"),
        SampleRecord("d", "s3", "study", "c", "c", None, "mouse", "heart", "snRNA", "MI", "myocardial_injury"),
        SampleRecord("d", "s4", "study", "d", "d", None, "mouse", "heart", "snRNA", "sham", "reference"),
    ]
    first = make_grouped_split(samples, seed=4, train_fraction=0.5, validation_fraction=0.25)
    second = make_grouped_split(samples, seed=4, train_fraction=0.5, validation_fraction=0.25)
    assert first == second
