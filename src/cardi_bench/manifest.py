"""Validation helpers for reproducible benchmark manifests."""
from __future__ import annotations

REQUIRED_SPLIT_KEYS = {"primary_group_key", "technical_replicates_together", "study_held_out_test"}
REQUIRED_GATES = {"require_verified_condition", "require_subject_identifier", "reject_group_leakage", "reject_technical_replicate_leakage"}


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    for key in ("benchmark_id", "version", "task", "dataset_ids", "split", "quality_gates", "evaluation"):
        if key not in manifest:
            errors.append(f"missing required field: {key}")
    split = manifest.get("split", {})
    errors.extend(f"missing split policy field: {key}" for key in sorted(REQUIRED_SPLIT_KEYS - split.keys()))
    gates = manifest.get("quality_gates", {})
    errors.extend(f"missing quality gate: {key}" for key in sorted(REQUIRED_GATES - gates.keys()))
    if manifest.get("private_test_labels") is not True:
        errors.append("private_test_labels must be true for locked-test benchmarks")
    if not manifest.get("dataset_ids"):
        errors.append("dataset_ids must not be empty")
    if not manifest.get("evaluation"):
        errors.append("evaluation metrics must not be empty")
    return errors


def assert_valid_manifest(manifest: dict) -> None:
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError("Invalid CardiBench manifest: " + "; ".join(errors))
