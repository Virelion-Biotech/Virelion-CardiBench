import pytest
from cardi_bench.contamination import (
    DatasetLineage,
    audit_pretraining_overlap,
    require_benchmark_independence,
    fit_transform_fold,
)


def lineage(name, unit, fingerprint="a"):
    return DatasetLineage(
        name,
        frozenset([fingerprint * 64]),
        frozenset([unit]),
        frozenset([name]),
        complete=True,
    )


def test_renaming_dataset_does_not_hide_fingerprint_or_donor_overlap():
    report = audit_pretraining_overlap(
        lineage("test", "donor"), [lineage("renamed", "other")], corpus_complete=True
    )
    assert report["status"] == "contaminated"
    assert not report["independent_claim_eligible"]


def test_unknown_corpus_never_proves_zero_shot_independence():
    with pytest.raises(ValueError, match="unknown"):
        require_benchmark_independence(lineage("test", "a"), [], corpus_complete=False)
    assert require_benchmark_independence(
        lineage("test", "a"), [lineage("train", "b", "b")], corpus_complete=True
    )


def test_transformer_fit_sees_only_train_rows():
    class Transformer:
        def fit(self, rows):
            self.rows = rows

        def transform(self, rows):
            return rows

    obj, train, test = fit_transform_fold(
        Transformer,
        train_values=[[1], [2]],
        heldout_values=[[999]],
        train_units=["a", "b"],
        heldout_units=["c"],
    )
    assert obj.rows == [[1], [2]] and test == [[999]]
    with pytest.raises(ValueError, match="overlap"):
        fit_transform_fold(
            Transformer,
            train_values=[[1]],
            heldout_values=[[2]],
            train_units=["a"],
            heldout_units=["a"],
        )
