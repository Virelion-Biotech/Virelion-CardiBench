"""Offline ingestion and integrity checks for CardiAtlas therapeutic evidence bundles.

The importer deliberately consumes an exported JSONL bundle. It does not silently
fetch remote repositories, infer missing evidence, or convert absent values to zero.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def load_atlas_bundle(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load a CardiAtlas JSONL export, rejecting malformed or duplicate records."""
    records: dict[str, dict[str, Any]] = {}
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"cannot read CardiAtlas bundle {path}: {exc}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON in {path}:{line_number}: {exc}") from exc
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise ValueError(f"record in {path}:{line_number} must be an object with an id")
        record_id = record["id"]
        if record_id in records:
            raise ValueError(f"duplicate CardiAtlas record id: {record_id}")
        if record.get("record_type") not in {"evidence", "therapeutic_product"}:
            raise ValueError(f"unsupported CardiAtlas record type for {record_id}")
        records[record_id] = record
    if not records:
        raise ValueError("CardiAtlas bundle contains no records")
    return records


def ingest_therapeutic_casebook(
    casebook_path: str | Path, atlas_bundle_path: str | Path
) -> dict[str, Any]:
    """Resolve every casebook product/evidence reference against an Atlas export."""
    casebook = _read_json(casebook_path)
    records = load_atlas_bundle(atlas_bundle_path)
    cases = casebook.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("casebook must contain a non-empty cases array")

    resolved_cases = []
    seen_case_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("each case must be a JSON object")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in seen_case_ids:
            raise ValueError(f"case_id must be non-empty and unique: {case_id!r}")
        seen_case_ids.add(case_id)
        refs = case.get("curated_record_refs")
        if not isinstance(refs, dict):
            raise ValueError(f"{case_id}: curated_record_refs are required")
        product_id = refs.get("product_record_id")
        evidence_ids = refs.get("evidence_record_ids")
        if not isinstance(product_id, str) or not isinstance(evidence_ids, list) or not evidence_ids:
            raise ValueError(f"{case_id}: product and evidence references are required")
        product = records.get(product_id)
        if product is None or product.get("record_type") != "therapeutic_product":
            raise ValueError(f"{case_id}: missing therapeutic product record {product_id}")
        if product.get("name") != case.get("product_name"):
            raise ValueError(f"{case_id}: product name does not match CardiAtlas record")
        product_evidence = set(product.get("evidence_ids", []))
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError(f"{case_id}: duplicate evidence references")
        if not set(evidence_ids) <= product_evidence:
            raise ValueError(f"{case_id}: casebook evidence refs are not linked from product")
        resolved_evidence = []
        for evidence_id in evidence_ids:
            evidence = records.get(evidence_id)
            if evidence is None or evidence.get("record_type") != "evidence":
                raise ValueError(f"{case_id}: missing evidence record {evidence_id}")
            if not evidence.get("source_identifier") or not evidence.get("citation") or not evidence.get("source_url"):
                raise ValueError(f"{case_id}: evidence {evidence_id} lacks source provenance")
            resolved_evidence.append(evidence)
        resolved_cases.append({
            "case": case,
            "product_record": product,
            "evidence_records": resolved_evidence,
        })

    return {
        "schema_version": "1.0",
        "benchmark_id": casebook.get("benchmark_id"),
        "casebook_version": casebook.get("version"),
        "source_repository": "Virelion-Biotech/Virelion-CardiAtlas",
        "source_record_count": len(records),
        "resolved_case_count": len(resolved_cases),
        "cases": resolved_cases,
        "evaluation_policy": {
            "unknown_is_not_zero": True,
            "source_type_must_remain_visible": True,
            "primary_endpoint_hierarchy_must_be_preserved": True,
            "subgroup_findings_must_not_override_primary_endpoint": True,
        },
    }


def write_ingested_casebook(
    casebook_path: str | Path, atlas_bundle_path: str | Path, output_path: str | Path
) -> dict[str, Any]:
    result = ingest_therapeutic_casebook(casebook_path, atlas_bundle_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result
