"""Fail-closed admission assessment for candidate benchmark cohorts.

Admission assessment is a control-plane gate. A ready result means metadata are
sufficient to construct a deterministic leakage-checked preview; it is not an
automatic scientific or clinical approval.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .materialize import materialize
from .policies import POLICIES
from .registry import Sample


@dataclass(frozen=True)
class AdmissionAssessment:
    ready_for_review: bool
    status: str
    policy: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    required_fields: tuple[str, ...]
    missing_by_field: Mapping[str, tuple[str, ...]]
    statistics: Mapping[str, Any]
    materialization_preview: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["blockers"] = list(self.blockers)
        value["warnings"] = list(self.warnings)
        value["required_fields"] = list(self.required_fields)
        value["missing_by_field"] = {
            k: list(v) for k, v in self.missing_by_field.items()
        }
        return value


def assess_admission(
    raw_samples: Iterable[Mapping[str, Any]],
    *,
    policy: str = "subject_heldout",
    benchmark_id: str = "candidate",
    version: str = "1.0",
    test_values: Iterable[str] = (),
    validation_values: Iterable[str] = (),
    seed: int = 0,
    benchmark_lineage=None,
    pretraining_lineage=(),
    pretraining_corpus_complete: bool = False,
    require_independence: bool = False,
) -> AdmissionAssessment:
    if policy not in POLICIES:
        return AdmissionAssessment(
            False,
            "blocked",
            policy,
            (f"unknown split policy: {policy}",),
            (),
            (),
            {},
            {},
        )

    rows = [dict(item) for item in raw_samples]
    blockers: list[str] = []
    warnings: list[str] = []
    policy_field = POLICIES[policy].primary_key
    required = tuple(
        dict.fromkeys(("sample_id", "group_id", "study_id", "label", policy_field))
    )
    missing: dict[str, tuple[str, ...]] = {}

    if not rows:
        blockers.append("candidate contains no samples")

    for field in required:
        absent = tuple(
            str(item.get("sample_id") or f"row-{index}")
            for index, item in enumerate(rows, 1)
            if item.get(field) is None or str(item.get(field)).strip() == ""
        )
        if absent:
            missing[field] = absent
            blockers.append(
                f"required metadata {field} missing for {len(absent)} samples"
            )

    ids = [str(item.get("sample_id") or "") for item in rows if item.get("sample_id")]
    duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
    if duplicates:
        blockers.append(f"duplicate sample IDs: {duplicates[:10]}")

    labels = [
        str(item.get("label") or "")
        for item in rows
        if item.get("label") not in (None, "")
    ]
    if rows and len(set(labels)) < 2:
        blockers.append("candidate has fewer than two explicit labels")

    test = {str(value) for value in test_values if str(value)}
    validation = {str(value) for value in validation_values if str(value)}
    if test & validation:
        blockers.append("test and validation values overlap")
    policy_values = {
        str(item.get(policy_field))
        for item in rows
        if item.get(policy_field) not in (None, "")
    }
    if policy != "subject_heldout" and not test:
        blockers.append(f"policy {policy} requires explicit test_values")
    unknown = (test | validation) - policy_values
    if unknown:
        blockers.append(f"unknown {policy_field} holdout values: {sorted(unknown)}")
    if rows and len(policy_values) < 2:
        blockers.append(
            f"policy {policy} has fewer than two distinct {policy_field} values"
        )

    samples: list[Sample] = []
    if not blockers:
        samples = [
            Sample(
                sample_id=str(item["sample_id"]),
                group_id=str(item["group_id"]),
                study_id=str(item["study_id"]),
                label=str(item["label"]),
                technical_group=str(item["technical_group"])
                if item.get("technical_group") not in (None, "")
                else None,
                organism=str(item["organism"])
                if item.get("organism") not in (None, "")
                else None,
                timepoint=str(item["timepoint"])
                if item.get("timepoint") not in (None, "")
                else None,
                cell_context=str(item["cell_context"])
                if item.get("cell_context") not in (None, "")
                else None,
                region=str(item["region"])
                if item.get("region") not in (None, "")
                else None,
            )
            for item in rows
        ]

    contamination = None
    if benchmark_lineage is not None:
        from .contamination import audit_pretraining_overlap

        contamination = audit_pretraining_overlap(
            benchmark_lineage,
            pretraining_lineage,
            corpus_complete=pretraining_corpus_complete,
        )
        if require_independence and not contamination["independent_claim_eligible"]:
            blockers.append("pretraining independence: " + contamination["status"])
    elif require_independence:
        blockers.append("pretraining independence: missing dataset lineage")
    preview = None
    if not blockers:
        try:
            locked = materialize(
                samples,
                benchmark_id=benchmark_id,
                version=version,
                policy=policy,
                test_values=test,
                validation_values=validation,
                seed=seed,
            )
            preview = locked.to_dict()
            evaluation_splits = {
                k: v
                for k, v in locked.label_counts.items()
                if k in {"validation", "test"}
            }
            if not evaluation_splits:
                blockers.append(
                    "materialization produced no validation or test partition"
                )
            for split, counts in evaluation_splits.items():
                if len([label for label, count in counts.items() if count > 0]) < 2:
                    blockers.append(f"{split} partition has fewer than two labels")
        except ValueError as exc:
            blockers.append(str(exc))

    statistics = {
        "pretraining_contamination": contamination,
        "samples": len(rows),
        "labels": dict(sorted(Counter(labels).items())),
        "policy_field": policy_field,
        "policy_values": len(policy_values),
        "studies": len(
            {
                str(item.get("study_id"))
                for item in rows
                if item.get("study_id") not in (None, "")
            }
        ),
        "groups": len(
            {
                str(item.get("group_id"))
                for item in rows
                if item.get("group_id") not in (None, "")
            }
        ),
    }
    if not blockers and any(item.get("technical_group") in (None, "") for item in rows):
        warnings.append(
            "technical replicate metadata are incomplete; absence is preserved as unknown"
        )
    ready = not blockers
    return AdmissionAssessment(
        ready_for_review=ready,
        status="ready_for_review" if ready else "blocked",
        policy=policy,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        required_fields=required,
        missing_by_field=missing,
        statistics=statistics,
        materialization_preview=preview,
    )
