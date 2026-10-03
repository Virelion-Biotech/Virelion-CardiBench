"""Conservative identity resolution for discovered cardiac benchmark evidence.

The resolver collapses records only when they share a strong identifier *and*
the same artifact type. Cross-type matches become explicit links rather than
silent merges; a paper DOI and a GEO dataset are related evidence, not the same
object.
"""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from typing import Any, Iterable, Mapping

from .evidence import CatalogRecord, IdentityLink, ResolvedCatalog, SourceObservation

IDENTIFIER_PRIORITY = (
    "doi",
    "geo",
    "bioproject",
    "sra",
    "pmid",
    "github",
    "url",
    "uri",
    "accession",
)


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _identity_key(observation: SourceObservation) -> tuple[str, str, str]:
    for name in IDENTIFIER_PRIORITY:
        value = observation.identifiers.get(name)
        if value:
            return observation.kind, name, value
    return observation.kind, "source", f"{observation.source}:{observation.source_record_id}"


def _record_id(key: tuple[str, str, str]) -> str:
    return f"cbx-{_digest(key)[:16]}"


def resolve_observations(
    observations: Iterable[SourceObservation],
    *,
    overrides: Mapping[str, str] | None = None,
) -> ResolvedCatalog:
    """Resolve observations into a catalog without over-merging related artifacts.

    ``overrides`` maps observation_id -> reviewer-selected record key. It is an
    explicit human override surface; absent an override, exact strong identity
    plus artifact kind is required for collapsing observations.
    """
    observations = list(observations)
    override_map = dict(overrides or {})
    grouped: dict[tuple[str, str, str], list[SourceObservation]] = defaultdict(list)

    for observation in observations:
        if observation.observation_id in override_map:
            key = (observation.kind, "reviewed", str(override_map[observation.observation_id]))
        else:
            key = _identity_key(observation)
        grouped[key].append(observation)

    records: list[CatalogRecord] = []
    identifier_to_records: dict[tuple[str, str], set[str]] = defaultdict(set)

    for key, items in sorted(grouped.items(), key=lambda pair: pair[0]):
        rid = _record_id(key)
        titles = sorted({item.title for item in items}, key=lambda value: (len(value), value.lower()))
        canonical_name = titles[0]
        aliases = tuple(title for title in titles[1:] if title != canonical_name)
        identifiers: dict[str, str] = {}
        conflicts: dict[str, list[str]] = {}
        by_identifier: dict[str, set[str]] = defaultdict(set)
        for item in items:
            for name, value in item.identifiers.items():
                by_identifier[name].add(value)
        for name, values in sorted(by_identifier.items()):
            if len(values) == 1:
                identifiers[name] = next(iter(values))
            else:
                conflicts[name] = sorted(values)

        metadata: dict[str, Any] = {
            "observation_count": len(items),
            "source_record_ids": sorted(f"{item.source}:{item.source_record_id}" for item in items),
        }
        if conflicts:
            metadata["identifier_conflicts"] = conflicts

        states = {item.evidence_state for item in items}
        evidence_state = "verified" if states == {"verified"} else ("observed" if "observed" in states else sorted(states)[0])
        record = CatalogRecord(
            record_id=rid,
            canonical_name=canonical_name,
            record_type=key[0],
            aliases=aliases,
            identifiers=identifiers,
            observation_ids=tuple(sorted(item.observation_id for item in items)),
            sources=tuple(sorted({item.source for item in items})),
            evidence_state=evidence_state,
            metadata=metadata,
        )
        records.append(record)
        for item in items:
            for name, value in item.identifiers.items():
                identifier_to_records[(name, value)].add(rid)

    links: set[tuple[str, str, str, str, str]] = set()
    for (name, value), record_ids in identifier_to_records.items():
        ids = sorted(record_ids)
        if len(ids) < 2:
            continue
        for index, left in enumerate(ids):
            for right in ids[index + 1 :]:
                links.add((left, right, "related_evidence", name, value))

    return ResolvedCatalog(
        records=tuple(sorted(records, key=lambda item: item.record_id)),
        links=tuple(
            IdentityLink(left_record_id=left,right_record_id=right,relation=relation,identifier_type=name,identifier_value=value)
            for left, right, relation, name, value in sorted(links)
        ),
    )
