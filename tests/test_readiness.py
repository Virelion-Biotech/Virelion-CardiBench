from cardi_bench import SampleRecord, assess_readiness


def sample(sample_id: str, subject: str, condition: str) -> SampleRecord:
    return SampleRecord(
        dataset_id="demo",
        sample_id=sample_id,
        study_id="study-a",
        subject_id=subject,
        biological_group=None,
        technical_group=None,
        organism="Mus musculus",
        tissue="heart",
        modality="single-nucleus RNA-seq",
        raw_condition=condition,
        normalized_label=condition,
    )


def test_ready_candidate_with_two_labels():
    report = assess_readiness([
        sample("s1", "a", "reference"),
        sample("s2", "b", "myocardial_injury"),
    ])
    assert report.ready
    assert report.score == 1.0


def test_unlabeled_candidate_is_blocked():
    record = sample("s1", "a", "reference")
    record = SampleRecord(**{**record.to_dict(), "normalized_label": None})
    report = assess_readiness([record])
    assert not report.ready
    assert report.blockers
