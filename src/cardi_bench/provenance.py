"""Hashes and provenance records for benchmark reproducibility."""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class ProvenanceRecord:
    source: str
    accession: str
    registry_version: str
    metadata_hash: str
    preprocessing_version: str
    manifest_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonicalize(value: Any) -> Any:
    """Normalize mappings and unordered record lists before hashing."""
    if isinstance(value, dict):
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        normalized = [_canonicalize(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return value


def canonical_metadata_hash(metadata: Any) -> str:
    payload = json.dumps(_canonicalize(metadata), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def make_provenance(*, source: str, accession: str, registry_version: str, metadata: dict[str, Any], preprocessing_version: str, manifest_version: str) -> ProvenanceRecord:
    if not source or not accession:
        raise ValueError("source and accession are required")
    return ProvenanceRecord(
        source=source,
        accession=accession,
        registry_version=registry_version,
        metadata_hash=canonical_metadata_hash(metadata),
        preprocessing_version=preprocessing_version,
        manifest_version=manifest_version,
    )
