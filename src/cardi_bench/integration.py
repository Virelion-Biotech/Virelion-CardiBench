"""Cross-stack serialization helpers without importing sibling services."""
from __future__ import annotations
from typing import Any, Mapping
from .admission import AdmissionAssessment
from .evidence import SourceObservation
from .result_history import BenchmarkResultObservation

def bridge_evidence_payload(observation:SourceObservation,*,trace:Mapping[str,Any])->dict[str,Any]:
    return {"observation_id":observation.observation_id,"kind":observation.kind,"source":observation.source,"source_record_id":observation.source_record_id,"title":observation.title,"uri":observation.url,"identifiers":dict(observation.identifiers),"evidence_state":observation.evidence_state,"observed_at":observation.observed_at,"published_at":observation.published_at,"trace":dict(trace)}
def bridge_result_payload(result:BenchmarkResultObservation,*,trace:Mapping[str,Any],artifacts:list[Mapping[str,Any]]|None=None)->dict[str,Any]:
    return {"result_id":result.result_id,"benchmark_id":result.benchmark_id,"benchmark_version":result.benchmark_version,"benchmark_provenance_sha256":result.benchmark_provenance_sha256,"model_id":result.model_id,"model_version":result.model_version,"split":result.split,"metrics":dict(result.metrics),"sample_count":result.sample_count,"protocol_id":result.protocol_id,"source":result.source,"recorded_at":result.recorded_at,"artifacts":[dict(item) for item in (artifacts or [])],"trace":dict(trace)}
def trace_metadata_for_discovery(observation:SourceObservation)->dict[str,Any]:
    return {"component":"CardiBench","operation":"benchmark.discovery","observation_id":observation.observation_id,"source":observation.source,"source_record_id":observation.source_record_id,"content_sha256":observation.content_sha256}
def trace_metadata_for_result(result:BenchmarkResultObservation)->dict[str,Any]:
    return {"component":"CardiBench","operation":"benchmark.result","result_id":result.result_id,"benchmark_id":result.benchmark_id,"benchmark_version":result.benchmark_version,"benchmark_provenance_sha256":result.benchmark_provenance_sha256,"comparability_key":result.comparability_key}

def bridge_admission_payload(
    assessment: AdmissionAssessment,
    *,
    benchmark_id: str,
    benchmark_version: str,
    trace: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "benchmark_id": benchmark_id,
        "benchmark_version": benchmark_version,
        "policy": assessment.policy,
        "status": assessment.status,
        "ready_for_review": assessment.ready_for_review,
        "blockers": list(assessment.blockers),
        "warnings": list(assessment.warnings),
        "required_fields": list(assessment.required_fields),
        "missing_by_field": {key: list(value) for key, value in assessment.missing_by_field.items()},
        "statistics": dict(assessment.statistics),
        "materialization_preview": (
            dict(assessment.materialization_preview)
            if assessment.materialization_preview is not None
            else None
        ),
        "trace": dict(trace),
    }

def trace_metadata_for_admission(
    assessment: AdmissionAssessment,
    *,
    benchmark_id: str,
    benchmark_version: str,
) -> dict[str, Any]:
    return {
        "component": "CardiBench",
        "operation": "benchmark.admission",
        "benchmark_id": benchmark_id,
        "benchmark_version": benchmark_version,
        "policy": assessment.policy,
        "status": assessment.status,
        "ready_for_review": assessment.ready_for_review,
        "blocker_count": len(assessment.blockers),
    }
