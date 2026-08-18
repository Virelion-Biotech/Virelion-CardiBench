from cardi_bench.manifest import validate_manifest


def test_mi_manifest_has_locked_test_and_leakage_gates():
    manifest = {
        "benchmark_id": "x",
        "version": "1",
        "task": "binary_classification",
        "dataset_ids": ["d1"],
        "split": {
            "primary_group_key": "biological_subject",
            "technical_replicates_together": True,
            "study_held_out_test": True,
        },
        "quality_gates": {
            "require_verified_condition": True,
            "require_subject_identifier": True,
            "reject_group_leakage": True,
            "reject_technical_replicate_leakage": True,
        },
        "evaluation": ["auroc"],
        "private_test_labels": True,
    }
    assert validate_manifest(manifest) == []


def test_manifest_rejects_unlocked_test():
    manifest = {
        "benchmark_id": "x",
        "version": "1",
        "task": "binary_classification",
        "dataset_ids": ["d1"],
        "split": {
            "primary_group_key": "subject",
            "technical_replicates_together": True,
            "study_held_out_test": True,
        },
        "quality_gates": {
            "require_verified_condition": True,
            "require_subject_identifier": True,
            "reject_group_leakage": True,
            "reject_technical_replicate_leakage": True,
        },
        "evaluation": ["auroc"],
        "private_test_labels": False,
    }
    assert any("private_test_labels" in error for error in validate_manifest(manifest))
