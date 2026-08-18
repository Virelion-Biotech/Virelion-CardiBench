import json
from pathlib import Path

from cardi_bench.cli import main


def test_validate_manifest_cli(tmp_path, monkeypatch, capsys):
    manifest = {
        "benchmark_id": "cli-test",
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
        "private_test_labels": True,
    }
    path = Path(tmp_path) / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["cardibench", "validate-manifest", str(path)])
    assert main() == 0
    assert "valid:" in capsys.readouterr().out
