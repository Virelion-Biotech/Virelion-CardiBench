import json

import pytest

from cardi_bench.therapeutic_evidence import ingest_therapeutic_casebook, write_ingested_casebook


def _fixtures(tmp_path):
    casebook = {
        "benchmark_id": "therapy-casebook",
        "version": "1.0",
        "cases": [{
            "case_id": "cardiamp",
            "product_name": "CardiAMP",
            "curated_record_refs": {
                "product_record_id": "product-cardiamp",
                "evidence_record_ids": ["evidence-cardiamp"],
            },
        }],
    }
    product = {
        "record_type": "therapeutic_product",
        "id": "product-cardiamp",
        "name": "CardiAMP",
        "evidence_ids": ["evidence-cardiamp"],
    }
    evidence = {
        "record_type": "evidence",
        "id": "evidence-cardiamp",
        "source_identifier": "PMID:123",
        "citation": "Example primary source",
        "source_url": "https://example.org/source",
        "context": {"source_class": "peer_reviewed"},
    }
    case_path = tmp_path / "casebook.json"
    bundle_path = tmp_path / "atlas.jsonl"
    case_path.write_text(json.dumps(casebook), encoding="utf-8")
    bundle_path.write_text("\n".join(json.dumps(x) for x in (product, evidence)) + "\n", encoding="utf-8")
    return case_path, bundle_path


def test_ingestion_resolves_product_and_source_provenance(tmp_path):
    casebook, bundle = _fixtures(tmp_path)
    result = ingest_therapeutic_casebook(casebook, bundle)
    assert result["resolved_case_count"] == 1
    assert result["cases"][0]["product_record"]["id"] == "product-cardiamp"
    assert result["cases"][0]["evidence_records"][0]["source_identifier"] == "PMID:123"


def test_ingestion_rejects_casebook_evidence_not_linked_to_product(tmp_path):
    casebook, bundle = _fixtures(tmp_path)
    raw = json.loads(casebook.read_text())
    raw["cases"][0]["curated_record_refs"]["evidence_record_ids"] = ["unknown"]
    casebook.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="not linked from product"):
        ingest_therapeutic_casebook(casebook, bundle)


def test_ingestion_rejects_duplicate_atlas_ids(tmp_path):
    casebook, bundle = _fixtures(tmp_path)
    lines = bundle.read_text().splitlines()
    bundle.write_text("\n".join(lines + [lines[0]]) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate CardiAtlas record id"):
        ingest_therapeutic_casebook(casebook, bundle)


def test_cli_output_is_reproducible_json(tmp_path):
    casebook, bundle = _fixtures(tmp_path)
    output = tmp_path / "out" / "ingested.json"
    result = write_ingested_casebook(casebook, bundle, output)
    assert json.loads(output.read_text())["benchmark_id"] == result["benchmark_id"]
