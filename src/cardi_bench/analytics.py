"""Coverage and comparability analytics for CardiBench intelligence products."""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .evidence import ResolvedCatalog
from .result_history import BenchmarkResultObservation

STRONG_IDENTIFIERS = {"doi", "geo", "sra", "bioproject", "pmid", "github", "accession"}


def catalog_coverage(catalog: ResolvedCatalog) -> dict[str, Any]:
    records = list(catalog.records)
    by_type = Counter(item.record_type for item in records)
    by_source = Counter(source for item in records for source in item.sources)
    by_state = Counter(item.evidence_state for item in records)
    with_identifier = sum(
        1 for item in records if STRONG_IDENTIFIERS.intersection(item.identifiers)
    )
    linked = {
        record_id
        for link in catalog.links
        for record_id in (link.left_record_id, link.right_record_id)
    }
    return {
        "records": len(records),
        "links": len(catalog.links),
        "by_type": dict(sorted(by_type.items())),
        "by_source": dict(sorted(by_source.items())),
        "by_evidence_state": dict(sorted(by_state.items())),
        "records_with_strong_identifier": with_identifier,
        "records_without_strong_identifier": len(records) - with_identifier,
        "records_with_cross_artifact_links": len(linked),
    }


def result_coverage(results: Iterable[BenchmarkResultObservation]) -> dict[str, Any]:
    items = list(results)
    groups: Counter[str] = Counter(item.comparability_key for item in items)
    metrics = Counter(metric for item in items for metric in item.metrics)
    return {
        "results": len(items),
        "benchmarks": len({(item.benchmark_id, item.benchmark_version) for item in items}),
        "models": len({(item.model_id, item.model_version) for item in items}),
        "comparability_groups": len(groups),
        "largest_comparability_group": max(groups.values(), default=0),
        "metrics": dict(sorted(metrics.items())),
        "evaluator_sources": dict(sorted(Counter(item.source for item in items).items())),
        "cross_protocol_pooling_forbidden": True,
    }


def intelligence_summary(
    catalog: ResolvedCatalog,
    results: Iterable[BenchmarkResultObservation] = (),
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "catalog_generated_at": catalog.generated_at,
        "catalog": catalog_coverage(catalog),
        "results": result_coverage(results),
    }
