"""Cross-stack serialization helpers without importing sibling services."""
from __future__ import annotations
from typing import Any, Mapping
from .evidence import SourceObservation
from .result_history import BenchmarkResultObservation

def bridge_evidence_payload(observation:SourceObservation,*,trace:Mapping[str,Any])->dict[str,Any]:
    return {"observation_id":observation.observation_id,"kind":observation.kind,"source":observation.source,"source_record_id":observation.source_record_id,"title":observation.title,"uri":observation.url,"identifiers":dict(observation.identifiers),"evidence_state":observation.evidence_state,"observed_at":observation.observed_at,"published_at":observation.published_at,"trace":dict(trace)}
def bridge_result_payload(result:BenchmarkResultObservation,*,trace:Mapping[str,Any],artifacts:list[Mapping[str,Any]]|None=None)->dict[str,Any]:
    return {"result_id":result.result_id,"benchmark_id":result.benchmark_id,"benchmark_version":result.benchmark_version,"benchmark_provenance_sha256":result.benchmark_provenance_sha256,"model_id":result.model_id,"model_version":result.model_version,"split":result.split,"metrics":dict(result.metrics),"sample_count":result.sample_count,"protocol_id":result.protocol_id,"recorded_at":result.recorded_at,"artifacts":[dict(item) for item in (artifacts or [])],"trace":dict(trace)}
def trace_metadata_for_discovery(observation:SourceObservation)->dict[str,Any]:
    return {"component":"CardiBench","operation":"benchmark.discovery","observation_id":observation.observation_id,"source":observation.source,"source_record_id":observation.source_record_id,"content_sha256":observation.content_sha256}
def trace_metadata_for_result(result:BenchmarkResultObservation)->dict[str,Any]:
    return {"component":"CardiBench","operation":"benchmark.result","result_id":result.result_id,"benchmark_id":result.benchmark_id,"benchmark_version":result.benchmark_version,"benchmark_provenance_sha256":result.benchmark_provenance_sha256,"comparability_key":result.comparability_key}
