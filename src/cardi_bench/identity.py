"""Conservative identity resolution for discovered cardiac benchmark evidence.

Same-type artifacts are collapsed only when they are connected by exact strong
identifiers or an explicit reviewer override. Cross-type matches remain
separate records linked as related evidence.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from typing import Any, Iterable, Mapping

from .evidence import CatalogRecord, IdentityLink, ResolvedCatalog, SourceObservation

IDENTIFIER_PRIORITY = (
    "doi", "geo", "bioproject", "sra", "pmid", "pmcid", "nct",
    "github", "url", "uri", "accession",
)

KIND_IDENTIFIER_PRIORITY = {
    "dataset": ("geo", "bioproject", "sra", "accession", "doi", "url", "uri"),
    "publication": ("doi", "pmid", "pmcid", "url", "uri"),
    "repository": ("github", "url", "uri", "doi"),
    "benchmark": ("doi", "github", "url", "uri", "accession"),
    "model": ("doi", "github", "url", "uri", "accession"),
    "other": IDENTIFIER_PRIORITY,
}


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _record_id(kind: str, identifier_name: str, identifier_value: str) -> str:
    return f"cbx-{_digest((kind, identifier_name, identifier_value))[:16]}"


def _primary_identity(kind: str, items: list[SourceObservation]) -> tuple[str, str]:
    values: dict[str, set[str]] = defaultdict(set)
    for item in items:
        for name, value in item.identifiers.items():
            values[name].add(value)
    for name in KIND_IDENTIFIER_PRIORITY.get(kind, IDENTIFIER_PRIORITY):
        if values.get(name):
            return name, sorted(values[name])[0]
    source_keys = sorted(f"{item.source}:{item.source_record_id}" for item in items)
    return "source", source_keys[0]


def resolve_observations(
    observations: Iterable[SourceObservation],
    *,
    overrides: Mapping[str, str] | None = None,
) -> ResolvedCatalog:
    """Resolve observations without over-merging related artifacts.

    Resolution is transitive within one artifact kind. If one dataset
    observation shares GEO with a second observation and that second shares DOI
    with a third, all three resolve to one dataset record. A paper with either
    identifier remains a separate publication record and is linked explicitly.

    The overrides mapping uses observation_id keys and reviewer-selected
    identity labels. Same-kind observations with the same reviewed label are
    forced into one component.
    """
    items = list(observations)
    override_map = {str(key): str(value) for key, value in dict(overrides or {}).items()}
    parent = list(range(len(items)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[b] = a

    identifier_owner: dict[tuple[str, str, str], int] = {}
    reviewed_owner: dict[tuple[str, str], int] = {}
    for index, item in enumerate(items):
        reviewed = override_map.get(item.observation_id)
        if reviewed:
            key = (item.kind, reviewed)
            union(index, reviewed_owner.setdefault(key, index))
        for name in IDENTIFIER_PRIORITY:
            value = item.identifiers.get(name)
            if value:
                key = (item.kind, name, value)
                union(index, identifier_owner.setdefault(key, index))

    components: dict[int, list[SourceObservation]] = defaultdict(list)
    for index, item in enumerate(items):
        components[find(index)].append(item)

    records: list[CatalogRecord] = []
    identifier_to_records: dict[tuple[str, str], set[str]] = defaultdict(set)

    for component in components.values():
        kind = component[0].kind
        identity_name, identity_value = _primary_identity(kind, component)
        rid = _record_id(kind, identity_name, identity_value)
        titles = sorted({item.title for item in component}, key=lambda value: (len(value), value.lower()))
        canonical_name = titles[0]
        aliases = tuple(title for title in titles[1:] if title != canonical_name)

        by_identifier: dict[str, set[str]] = defaultdict(set)
        for item in component:
            for name, value in item.identifiers.items():
                by_identifier[name].add(value)
                identifier_to_records[(name, value)].add(rid)

        identifiers: dict[str, str] = {}
        conflicts: dict[str, list[str]] = {}
        for name, values in sorted(by_identifier.items()):
            if len(values) == 1:
                identifiers[name] = next(iter(values))
            else:
                conflicts[name] = sorted(values)

        metadata: dict[str, Any] = {
            "observation_count": len(component),
            "source_record_ids": sorted(f"{item.source}:{item.source_record_id}" for item in component),
            "identity_basis": {"identifier_type": identity_name, "identifier_value": identity_value},
        }
        if conflicts:
            metadata["identifier_conflicts"] = conflicts

        states = {item.evidence_state for item in component}
        evidence_state = (
            "verified" if states == {"verified"} else
            "observed" if "observed" in states else
            "unverified" if "unverified" in states else
            "unknown" if "unknown" in states else
            "not_applicable"
        )
        records.append(CatalogRecord(
            record_id=rid,
            canonical_name=canonical_name,
            record_type=kind,
            aliases=aliases,
            identifiers=identifiers,
            observation_ids=tuple(sorted(item.observation_id for item in component)),
            sources=tuple(sorted({item.source for item in component})),
            evidence_state=evidence_state,
            metadata=metadata,
        ))

    links: set[tuple[str, str, str, str, str]] = set()
    for (name, value), record_ids in identifier_to_records.items():
        ids = sorted(record_ids)
        for position, left in enumerate(ids):
            for right in ids[position + 1:]:
                links.add((left, right, "related_evidence", name, value))

    return ResolvedCatalog(
        records=tuple(sorted(records, key=lambda item: item.record_id)),
        links=tuple(IdentityLink(
            left_record_id=left,
            right_record_id=right,
            relation=relation,
            identifier_type=name,
            identifier_value=value,
        ) for left, right, relation, name, value in sorted(links)),
    )
