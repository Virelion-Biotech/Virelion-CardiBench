from pathlib import Path


def test_reference_evaluation_workflow_is_pinned_and_nonclinical():
    script=Path("scripts/generate_reference_result.py").read_text(encoding="utf-8")
    workflow=Path(".github/workflows/reference-evaluation.yml").read_text(encoding="utf-8")
    assert "scientific_use" in script
    assert "prohibited" in script
    assert "requires_authoritative_labels=True" in script
    assert "a697906c4ff68bacfaf764eda566a92a67cb64f3" in workflow
    assert "CardiEval software reference" in workflow
