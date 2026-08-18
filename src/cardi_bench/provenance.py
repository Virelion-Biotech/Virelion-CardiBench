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


def canonical_metadata_hash(metadata: dict[str, Any]) -> str:
    payload = json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
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
