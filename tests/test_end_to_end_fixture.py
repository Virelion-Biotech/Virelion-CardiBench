import json
from pathlib import Path

from cardi_bench import adapt_geo_samples, assess_dataset, make_grouped_split, canonical_metadata_hash


def test_fixture_metadata_to_split_pipeline():
    path = Path(__file__).parents[1] / "examples" / "fixtures" / "mi_sham_metadata.json"
    records = json.loads(path.read_text(encoding="utf-8"))
    adapted = adapt_geo_samples(records, study_id="fixture_mi")
    assert not adapted.rejected
    assert len(adapted.samples) == 4
    assert {sample.label for sample in adapted.samples} == {"myocardial_injury", "reference"}

    assignments = {sample.sample_id: "test" if sample.sample_id == "S4" else "train" for sample in adapted.samples}
    # Quality assessment must tolerate a deliberately small fixture while still
    # detecting unresolved labels and biological-group leakage.
    report = assess_dataset([
        type("R", (), {
            "sample_id": s.sample_id,
            "study_id": s.study_id,
            "subject_id": s.group_id,
            "biological_group": s.group_id,
            "technical_group": s.technical_group,
            "normalized_label": s.label,
        })() for s in adapted.samples
    ], assignments)
    assert report.passed
    assert canonical_metadata_hash(records) == canonical_metadata_hash(list(reversed(records)))


def test_grouped_split_keeps_subjects_together():
    records = [
        type("R", (), {"sample_id":"a1","study_id":"s","subject_id":"x","biological_group":None})(),
        type("R", (), {"sample_id":"a2","study_id":"s","subject_id":"x","biological_group":None})(),
        type("R", (), {"sample_id":"b1","study_id":"s","subject_id":"y","biological_group":None})(),
        type("R", (), {"sample_id":"c1","study_id":"s","subject_id":"z","biological_group":None})(),
    ]
    assignments = make_grouped_split(records, seed=4)
    assert assignments["a1"] == assignments["a2"]
