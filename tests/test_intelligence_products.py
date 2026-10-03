from pathlib import Path

from cardi_bench import (
    BenchmarkResultObservation,
    CatalogRecord,
    ResolvedCatalog,
    build_release_bundle,
    intelligence_summary,
    render_dashboard,
)
from cardi_bench.intelligence_store import save_catalog
from cardi_bench.result_history import save_result_history


def _catalog():
    return ResolvedCatalog(records=(
        CatalogRecord(
            record_id="cbx-1",
            canonical_name="<Cardiac & benchmark>",
            record_type="dataset",
            identifiers={"geo": "GSE1"},
            observation_ids=("obs-1",),
            sources=("geo",),
            evidence_state="verified",
        ),
        CatalogRecord(
            record_id="cbx-2",
            canonical_name="Cardiac model",
            record_type="model",
            sources=("github",),
            evidence_state="observed",
        ),
    ), generated_at="2026-10-03T00:00:00+00:00")


def _results():
    return [
        BenchmarkResultObservation(
            benchmark_id="b",
            benchmark_version="1",
            model_id="m",
            model_version="1",
            split="test",
            metrics={"auroc": 0.8},
            sample_count=20,
            benchmark_provenance_sha256="a" * 64,
            protocol_id="task",
            source="CardiEval/0.4",
            recorded_at="2026-10-03T00:00:00+00:00",
        )
    ]


def test_intelligence_summary_preserves_coverage_and_comparability():
    report=intelligence_summary(_catalog(),_results())
    assert report["catalog"]["records"]==2
    assert report["catalog"]["records_with_strong_identifier"]==1
    assert report["results"]["comparability_groups"]==1
    assert report["results"]["cross_protocol_pooling_forbidden"] is True


def test_release_bundle_is_content_deterministic(tmp_path: Path):
    catalog_path=tmp_path/"catalog.json"
    results_path=tmp_path/"results.json"
    save_catalog(catalog_path,_catalog())
    save_result_history(results_path,_results())
    first=build_release_bundle(catalog_path,results_path=results_path)
    second=build_release_bundle(catalog_path,results_path=results_path)
    assert first["release_id"]==second["release_id"]
    assert len(first["catalog_sha256"])==64
    assert len(first["results_sha256"])==64


def test_dashboard_is_read_only_and_escapes_catalog_text():
    html=render_dashboard(_catalog(),_results(),release={"release_id":"release-1"})
    assert "Read-only discovery" in html
    assert "&lt;Cardiac &amp; benchmark&gt;" in html
    assert "<Cardiac & benchmark>" not in html
    assert "CardiEval/0.4" in html
    assert "window.CARDIBENCH_SUMMARY" in html
