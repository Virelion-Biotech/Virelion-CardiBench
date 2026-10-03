"""Typed evidence records for CardiBench discovery and cataloging.

Discovery observations are deliberately separate from benchmark manifests. An
observation says only that a source exposed a record. Scientific readiness is
decided later by CardiBench's existing reconciliation, quality and readiness
layers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping

EVIDENCE_STATES = {"observed", "verified", "unknown", "not_applicable", "unverified"}
ARTIFACT_KINDS = {"dataset", "publication", "repository", "benchmark", "model", "other"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def normalize_identifier_map(values: Mapping[str, str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw_key, raw_value in dict(values or {}).items():
        key = str(raw_key).strip().lower()
        value = str(raw_value).strip()
        if not key or not value:
            continue
        if key == "doi":
            value = value.lower().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
        elif key in {"geo", "sra", "bioproject", "accession"}:
            value = value.upper()
        elif key == "pmid":
            value = re_digits(value)
        elif key in {"github", "url", "uri"}:
            value = value.rstrip("/")
        out[key] = value
    return dict(sorted(out.items()))


def re_digits(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    return digits or value


@dataclass(frozen=True)
class SourceObservation:
    source: str
    source_record_id: str
    title: str
    kind: str = "other"
    url: str | None = None
    published_at: str | None = None
    observed_at: str = field(default_factory=_now_iso)
    identifiers: Mapping[str, str] = field(default_factory=dict)
    text: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    evidence_state: str = "observed"
    observation_id: str = ""

    def __post_init__(self) -> None:
        source = self.source.strip().lower()
        record_id = self.source_record_id.strip()
        title = self.title.strip()
        kind = self.kind.strip().lower()
        state = self.evidence_state.strip().lower()
        if not source or not record_id or not title:
            raise ValueError("source, source_record_id and title are required")
        if kind not in ARTIFACT_KINDS:
            kind = "other"
        if state not in EVIDENCE_STATES:
            raise ValueError(f"Unsupported evidence_state: {self.evidence_state}")
        identifiers = normalize_identifier_map(self.identifiers)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "source_record_id", record_id)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "evidence_state", state)
        object.__setattr__(self, "identifiers", identifiers)
        if not self.observation_id:
            identity = {
                "source": source,
                "source_record_id": record_id,
                "kind": kind,
                "url": (self.url or "").rstrip("/"),
            }
            object.__setattr__(self, "observation_id", f"obs-{_stable_digest(identity)[:20]}")

    @property
    def content_sha256(self) -> str:
        payload = asdict(self)
        payload["identifiers"] = dict(self.identifiers)
        payload["metadata"] = dict(self.metadata)
        payload.pop("observed_at", None)
        return _stable_digest(payload)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["identifiers"] = dict(self.identifiers)
        value["metadata"] = dict(self.metadata)
        value["content_sha256"] = self.content_sha256
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SourceObservation":
        data = dict(value)
        data.pop("content_sha256", None)
        return cls(**data)


@dataclass(frozen=True)
class IdentityLink:
    left_record_id: str
    right_record_id: str
    relation: str
    identifier_type: str
    identifier_value: str
    status: str = "observed"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class CatalogRecord:
    record_id: str
    canonical_name: str
    record_type: str
    aliases: tuple[str, ...] = ()
    identifiers: Mapping[str, str] = field(default_factory=dict)
    observation_ids: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    evidence_state: str = "observed"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["aliases"] = list(self.aliases)
        value["identifiers"] = dict(self.identifiers)
        value["observation_ids"] = list(self.observation_ids)
        value["sources"] = list(self.sources)
        value["metadata"] = dict(self.metadata)
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CatalogRecord":
        data = dict(value)
        data["aliases"] = tuple(data.get("aliases") or ())
        data["observation_ids"] = tuple(data.get("observation_ids") or ())
        data["sources"] = tuple(data.get("sources") or ())
        return cls(**data)


@dataclass(frozen=True)
class ResolvedCatalog:
    records: tuple[CatalogRecord, ...]
    links: tuple[IdentityLink, ...] = ()
    generated_at: str = field(default_factory=_now_iso)
    schema_version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "records": [item.to_dict() for item in self.records],
            "links": [item.to_dict() for item in self.links],
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ResolvedCatalog":
        return cls(
            records=tuple(CatalogRecord.from_dict(item) for item in value.get("records", [])),
            links=tuple(IdentityLink(**item) for item in value.get("links", [])),
            generated_at=str(value.get("generated_at") or _now_iso()),
            schema_version=str(value.get("schema_version") or "1.0"),
        )
