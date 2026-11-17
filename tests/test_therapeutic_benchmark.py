import copy
import pytest
from cardi_bench.therapeutic_benchmark import (
    TherapeuticBenchmarkError, build_source_manifest, compare_strata_summary,
    validate_evidence_record, validate_manifest,
)

def record(**overrides):
    value = {
        "record_id":"study-a-endpoint-1","stratum":"myocardial_regeneration","modality":"modified_mRNA",
        "intervention":"transient MYC-Cyclin T1 modified mRNA","comparator":"vehicle control",
        "species":"Mus musculus","model":"adult mouse LAD myocardial infarction",
        "study_id":"doi:10.example/a","study_family_id":"family-a","biological_unit":"animal",
        "sample_size":{"n_total":12,"unit":"animals in this arm"},
        "dose_route_timing":"intramyocardial injection, day 0; dose per primary paper",
        "endpoint":"cardiomyocyte number","endpoint_definition":"Blinded stereological estimate of cardiomyocyte number per defined ventricular region.",
        "assay":"stereology","timepoint":"day 5","effect_estimate":{"status":"reported","value":1.2,"unit":"fold_change"},
        "uncertainty":{"status":"reported","type":"95% CI","lower":1.0,"upper":1.4},
        "adverse_events":{"ascertainment":"systematic","findings":"reported in source"},
        "risk_of_bias":{"randomization":"unclear","blinding":"partial","overall":"some_concerns"},
        "primary_source":"Primary peer-reviewed research article","source_identifier":"DOI:10.example/a",
        "source_url":"https://example.org/a","source_sha256":"a"*64,
        "curation_status":"primary_source_adjudicated","analysis_population":"all randomized animals",
        "randomization":"reported","blinding":"reported","multiplicity":"not_reported","follow_up":"5 days"
    }
    value.update(overrides)
    return value

def manifest(records):
    return {"schema_version":"1.0","benchmark_id":"test","version":"1.0.0","purpose":"test","records":records,
            "pooling_policy":{"cross_stratum_pooling":False,"cross_species_pooling":False,"cross_model_pooling":False}}

def test_valid_record_and_manifest():
    r=record()
    assert validate_evidence_record(r)==[]
    assert validate_manifest(manifest([r]))["record_count"]==1

def test_missing_denominator_and_primary_source_fail_closed():
    r=record(); del r["sample_size"]; del r["primary_source"]
    errors=validate_evidence_record(r)
    assert any("sample_size" in e for e in errors)
    assert any("primary_source" in e for e in errors)

def test_unadjudicated_candidate_cannot_be_admitted():
    assert any("primary_source_adjudicated" in e for e in validate_evidence_record(record(curation_status="candidate")))

def test_cross_stratum_study_family_is_rejected():
    a=record()
    b=record(record_id="study-a-endpoint-2",stratum="genetic_disease_modification")
    with pytest.raises(TherapeuticBenchmarkError,match="multiple strata"):
        validate_manifest(manifest([a,b]))

def test_duplicate_record_ids_are_rejected():
    a=record()
    with pytest.raises(TherapeuticBenchmarkError,match="duplicate record_id"):
        validate_manifest(manifest([a,copy.deepcopy(a)]))

def test_pooling_policy_must_fail_closed():
    p=manifest([record()]); p["pooling_policy"]["cross_species_pooling"]=True
    with pytest.raises(TherapeuticBenchmarkError,match="prohibit"):
        validate_manifest(p)

def test_source_manifest_is_deterministic_and_keeps_lineage():
    a=record()
    first=build_source_manifest([a]); second=build_source_manifest([a])
    assert first==second
    assert first["sources"][0]["source_sha256"]=="a"*64

def test_strata_summary_does_not_pool_effects():
    a=record()
    b=record(record_id="record-b",stratum="vascular_tissue_engineering",study_id="study-b",study_family_id="family-b",species="Sus scrofa",model="vascular graft model")
    summary=compare_strata_summary(manifest([a,b]))
    assert set(summary)=={"myocardial_regeneration","vascular_tissue_engineering"}
    assert "pooled_effect" not in str(summary)


def test_boolean_sample_size_is_not_accepted_as_an_integer():
    errors = validate_evidence_record(record(sample_size={"n_total": True, "unit": "animals"}))
    assert any("positive integer" in error for error in errors)
