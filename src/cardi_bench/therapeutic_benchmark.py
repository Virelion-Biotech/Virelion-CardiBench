"""Curation-first cardiac therapeutic evidence benchmark.

This layer is intentionally separate from sample-level ML benchmark manifests.
It validates study-level evidence records and prevents cross-stratum pooling.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
STRATA = {"myocardial_regeneration", "myocardial_repair_preservation", "genetic_disease_modification", "vascular_tissue_engineering"}
REQUIRED = {
    "record_id", "stratum", "modality", "intervention", "comparator", "species",
    "model", "study_id", "study_family_id", "biological_unit", "sample_size",
    "dose_route_timing", "endpoint", "endpoint_definition", "assay", "timepoint",
    "effect_estimate", "uncertainty", "adverse_events", "risk_of_bias",
    "primary_source", "source_identifier", "source_url", "source_sha256",
    "curation_status",
}
SHA256 = set("0123456789abcdef")

class TherapeuticBenchmarkError(ValueError):
    """Raised when an evidence record or manifest fails closed validation."""

def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def validate_evidence_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    for key in sorted(REQUIRED - record.keys()):
        errors.append(f"missing required field: {key}")
    if errors:
        return errors
    if record["stratum"] not in STRATA:
        errors.append(f"unsupported stratum: {record['stratum']!r}")
    for key in ("record_id","modality","intervention","comparator","species","model","study_id","study_family_id","biological_unit","dose_route_timing","endpoint","endpoint_definition","assay","timepoint","primary_source","source_identifier","source_url"):
        if not _nonempty(record.get(key)):
            errors.append(f"{key} must be a non-empty string")
    n = record.get("sample_size")
    if not isinstance(n, dict) or not isinstance(n.get("n_total"), int) or isinstance(n.get("n_total"), bool) or n["n_total"] <= 0:
        errors.append("sample_size.n_total must be a positive integer")
    if not isinstance(n, dict) or not _nonempty(n.get("unit")):
        errors.append("sample_size.unit must identify the denominator unit")
    if not isinstance(record.get("endpoint_definition"), str) or len(record["endpoint_definition"].strip()) < 20:
        errors.append("endpoint_definition must be operationally explicit (at least 20 characters)")
    digest = record.get("source_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in SHA256 for c in digest.lower()):
        errors.append("source_sha256 must be a 64-character SHA-256 hex digest")
    if record.get("curation_status") != "primary_source_adjudicated":
        errors.append("curation_status must be primary_source_adjudicated")
    if not isinstance(record.get("effect_estimate"), dict) or not record["effect_estimate"]:
        errors.append("effect_estimate must be an explicit object; use status=not_reported rather than inventing a value")
    if not isinstance(record.get("uncertainty"), dict) or not record["uncertainty"]:
        errors.append("uncertainty must be explicit; record unavailable uncertainty as status=not_reported")
    if not isinstance(record.get("adverse_events"), dict):
        errors.append("adverse_events must be an object with ascertainment and findings/status")
    if not isinstance(record.get("risk_of_bias"), dict) or not record["risk_of_bias"]:
        errors.append("risk_of_bias assessment is required")
    for key in ("analysis_population", "randomization", "blinding", "multiplicity", "follow_up"):
        if key not in record:
            errors.append(f"missing required design/interpretation field: {key}")
    return errors

def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise TherapeuticBenchmarkError("manifest must be an object")
    required = ("schema_version","benchmark_id","version","purpose","records","pooling_policy")
    missing = [k for k in required if k not in manifest]
    if missing:
        raise TherapeuticBenchmarkError("missing manifest fields: " + ", ".join(missing))
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise TherapeuticBenchmarkError("unsupported schema_version")
    if not isinstance(manifest["records"], list):
        raise TherapeuticBenchmarkError("records must be an array")
    ids: set[str] = set()
    families: dict[str, set[str]] = {}
    all_errors=[]
    for i, record in enumerate(manifest["records"]):
        errs=validate_evidence_record(record)
        if errs:
            all_errors.extend(f"records[{i}]: {e}" for e in errs)
            continue
        rid=record["record_id"]
        if rid in ids: all_errors.append(f"duplicate record_id: {rid}")
        ids.add(rid)
        families.setdefault(record["study_family_id"], set()).add(record["stratum"])
    for family, strata in families.items():
        if len(strata)>1:
            all_errors.append(f"study_family_id {family!r} appears in multiple strata; adjudicate or split source records explicitly")
    policy=manifest["pooling_policy"]
    if not isinstance(policy, dict) or policy.get("cross_stratum_pooling") is not False or policy.get("cross_species_pooling") is not False or policy.get("cross_model_pooling") is not False:
        all_errors.append("pooling_policy must explicitly prohibit cross-stratum, cross-species and cross-model pooling")
    if all_errors:
        raise TherapeuticBenchmarkError("\n".join(all_errors))
    return {"valid":True,"schema_version":SCHEMA_VERSION,"benchmark_id":manifest["benchmark_id"],"version":manifest["version"],"record_count":len(manifest["records"]),"strata":sorted({r["stratum"] for r in manifest["records"]}),"study_families":len(families)}

def load_manifest(path: str | Path) -> dict[str, Any]:
    try: return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: raise TherapeuticBenchmarkError(f"cannot read manifest: {exc}") from exc

def build_source_manifest(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Create deterministic source inventory; does not fetch or hash remote URLs."""
    rows=[]
    for record in records:
        errs=validate_evidence_record(record)
        if errs: raise TherapeuticBenchmarkError(f"{record.get('record_id','<unknown>')}: " + "; ".join(errs))
        rows.append({"record_id":record["record_id"],"study_id":record["study_id"],"study_family_id":record["study_family_id"],"source_identifier":record["source_identifier"],"source_url":record["source_url"],"source_sha256":record["source_sha256"]})
    rows.sort(key=lambda x:x["record_id"])
    payload=json.dumps(rows,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    return {"schema_version":SCHEMA_VERSION,"sources":rows,"inventory_sha256":hashlib.sha256(payload).hexdigest()}

def compare_strata_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    """Counts only; deliberately emits no cross-stratum winner or pooled effect."""
    validate_manifest(manifest)
    summary={}
    for r in manifest["records"]:
        key=r["stratum"]
        summary.setdefault(key,{"records":0,"species":{},"models":{},"study_families":set()})
        s=summary[key]; s["records"]+=1
        s["species"][r["species"]]=s["species"].get(r["species"],0)+1
        s["models"][r["model"]]=s["models"].get(r["model"],0)+1
        s["study_families"].add(r["study_family_id"])
    return {k:{**v,"study_families":len(v["study_families"])} for k,v in sorted(summary.items())}
