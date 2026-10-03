"""Adapters for converting GEO-like sample metadata into CardiBench records."""
from __future__ import annotations
from dataclasses import dataclass
import re
from .registry import Sample

@dataclass(frozen=True)
class AdapterResult:
    samples: tuple[Sample, ...]
    warnings: tuple[str, ...]
    rejected: tuple[str, ...]

_LABEL_PATTERNS = (
    ("ischemia_reperfusion", re.compile(r"\b(i/?r|ischemia[-_ ]reperfusion|reperfusion)\b", re.I)),
    ("myocardial_injury", re.compile(r"\b(mi|myocardial\s+infarction|infarct|injury|ischemi[ac])\b", re.I)),
    ("reference", re.compile(r"\b(sham|control|ctl|healthy|normal|reference)\b", re.I)),
)


def normalize_condition(text: str) -> tuple[str | None, str]:
    """Map free-text condition metadata to a controlled CardiBench label.

    Returns (label, status), where status is verified, ambiguous, or unknown.
    """
    matches = [label for label, pattern in _LABEL_PATTERNS if pattern.search(text or "")]
    if len(matches) == 1:
        return matches[0], "verified"
    if len(matches) > 1:
        return None, "ambiguous"
    return None, "unknown"


def adapt_geo_samples(records: list[dict[str, str]], *, study_id: str) -> AdapterResult:
    """Convert simple GEO sample metadata dictionaries into safe sample records."""
    samples: list[Sample] = []
    warnings: list[str] = []
    rejected: list[str] = []
    for record in records:
        sample_id = record.get("sample_id", "").strip()
        if not sample_id:
            rejected.append("missing sample_id")
            continue
        raw = " ".join([
            record.get("title", ""),
            record.get("source_name", ""),
            record.get("characteristics", ""),
            record.get("condition", ""),
        ]).strip()
        label, status = normalize_condition(raw)
        if status == "ambiguous":
            rejected.append(f"{sample_id}: ambiguous condition label")
            continue
        if status == "unknown":
            warnings.append(f"{sample_id}: condition could not be normalized")
            continue
        group_id = record.get("subject_id") or record.get("animal_id") or record.get("donor_id") or record.get("sample_group")
        if not group_id:
            rejected.append(f"{sample_id}: missing biological grouping identifier")
            continue
        samples.append(Sample(
            sample_id=sample_id,
            group_id=group_id,
            study_id=study_id,
            label=label,
            technical_group=record.get("technical_group") or record.get("library_id"),
            organism=record.get("organism") or record.get("species"),
            timepoint=record.get("timepoint") or record.get("time_point") or record.get("harvest_timepoint"),
            cell_context=record.get("cell_context") or record.get("cell_type"),
            region=record.get("region") or record.get("tissue_region"),
        ))
    return AdapterResult(tuple(samples), tuple(warnings), tuple(rejected))
