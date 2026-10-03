from cardi_bench import assess_admission


def _rows():
    return [
        {"sample_id":"s1","group_id":"g1","study_id":"st1","label":"reference"},
        {"sample_id":"s2","group_id":"g2","study_id":"st1","label":"myocardial_injury"},
        {"sample_id":"s3","group_id":"g3","study_id":"st1","label":"reference"},
        {"sample_id":"s4","group_id":"g4","study_id":"st1","label":"myocardial_injury"},
        {"sample_id":"s5","group_id":"g5","study_id":"st1","label":"reference"},
        {"sample_id":"s6","group_id":"g6","study_id":"st1","label":"myocardial_injury"},
    ]


def test_admission_ready_only_after_leakage_safe_materialization():
    report=assess_admission(_rows(),benchmark_id="fixture",seed=7,test_values=["g1","g2"],validation_values=["g3","g4"])
    assert report.ready_for_review
    assert report.status=="ready_for_review"
    assert report.materialization_preview
    assert set(report.materialization_preview["assignments"])=={row["sample_id"] for row in _rows()}


def test_admission_fails_closed_on_missing_subject_group():
    rows=_rows()
    rows[0]["group_id"]=""
    report=assess_admission(rows)
    assert not report.ready_for_review
    assert "group_id" in report.missing_by_field


def test_policy_specific_metadata_is_required():
    rows=[{**row,"organism":None} for row in _rows()]
    report=assess_admission(rows,policy="species_heldout",test_values=["Mus musculus"])
    assert not report.ready_for_review
    assert "organism" in report.missing_by_field


def test_non_subject_holdout_requires_explicit_test_values():
    rows=[{**row,"organism":"Mus musculus" if i<3 else "Homo sapiens"} for i,row in enumerate(_rows())]
    report=assess_admission(rows,policy="species_heldout")
    assert not report.ready_for_review
    assert any("explicit test_values" in item for item in report.blockers)
