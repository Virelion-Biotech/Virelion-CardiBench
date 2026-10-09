"""Training-exposure audits: absence of known overlap is not proof of independence."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DatasetLineage:
    dataset_id: str
    fingerprints: frozenset[str]
    biological_units: frozenset[str]
    study_ids: frozenset[str]
    preprocessing_fit_units: frozenset[str] = frozenset()
    complete: bool = False

    def __post_init__(self):
        for name in [
            "fingerprints",
            "biological_units",
            "study_ids",
            "preprocessing_fit_units",
        ]:
            items = frozenset(getattr(self, name))
            object.__setattr__(self, name, items)
            if any(not isinstance(x, str) or not x.strip() for x in items):
                raise ValueError(f"{name} must contain nonblank identifiers")
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must not be blank")
        if any(
            len(x) != 64 or any(c not in "0123456789abcdef" for c in x)
            for x in self.fingerprints
        ):
            raise ValueError("fingerprints must be SHA-256 digests")
        if self.complete and not all(
            [self.fingerprints, self.biological_units, self.study_ids]
        ):
            raise ValueError(
                "Complete lineage requires fingerprints, biological units and studies"
            )


def audit_pretraining_overlap(
    benchmark: DatasetLineage,
    training: Iterable[DatasetLineage],
    *,
    corpus_complete=False,
):
    training = tuple(training)
    overlaps = []
    for source in training:
        shared = {
            name: sorted(getattr(benchmark, name) & getattr(source, name))
            for name in ["fingerprints", "biological_units", "study_ids"]
        }
        shared["preprocessing_fit_units"] = sorted(
            benchmark.biological_units & source.preprocessing_fit_units
        )
        if any(shared.values()):
            overlaps.append({"training_dataset": source.dataset_id, "shared": shared})
    complete = bool(
        corpus_complete and benchmark.complete and all(x.complete for x in training)
    )
    return {
        "status": "contaminated"
        if overlaps
        else ("no_known_overlap" if complete else "unknown"),
        "overlaps": overlaps,
        "corpus_complete": complete,
        "independent_claim_eligible": complete and not overlaps,
        "scope": "Declared identifiers only; related studies/lab reuse still require curator review.",
    }


def require_benchmark_independence(benchmark, training, *, corpus_complete=False):
    report = audit_pretraining_overlap(
        benchmark, training, corpus_complete=corpus_complete
    )
    if not report["independent_claim_eligible"]:
        raise ValueError("Benchmark independence is " + report["status"])
    return report


def fit_transform_fold(
    factory, *, train_values, heldout_values, train_units, heldout_units
):
    """Instantiate and fit only on the training fold; return fitted artifact + transforms.

    The caller must retain the fitted transformer with its fold manifest. This
    helper cannot sanitize values that were already globally normalized.
    """
    train_units = tuple(train_units)
    heldout_units = tuple(heldout_units)
    if len(train_units) != len(train_values) or len(heldout_units) != len(
        heldout_values
    ):
        raise ValueError("Every row requires a biological unit ID")
    if not train_units or any(
        not str(x).strip() for x in (*train_units, *heldout_units)
    ):
        raise ValueError("Training fold and biological unit IDs must be nonempty")
    if set(train_units) & set(heldout_units):
        raise ValueError("Biological units overlap across preprocessing folds")
    transformer = factory()
    transformer.fit(train_values)
    return (
        transformer,
        transformer.transform(train_values),
        transformer.transform(heldout_values),
    )
