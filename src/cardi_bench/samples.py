"""Normalized cardiac benchmark sample records and phenotype ontology."""
from __future__ import annotations
from dataclasses import dataclass, asdict

CARDIAC_LABELS = (
    "reference", "myocardial_injury", "ischemia_reperfusion", "remodeling",
    "inflammatory", "hypertrophic", "metabolic", "electrophysiologic",
    "fibrotic", "cell_state", "pathogen_associated",
)


@dataclass(frozen=True)
class SampleRecord:
    dataset_id: str
    sample_id: str
    study_id: str
    subject_id: str | None
    biological_group: str | None
    technical_group: str | None
    organism: str
    tissue: str
    modality: str
    raw_condition: str
    normalized_label: str | None = None
    timepoint: str | None = None
    region: str | None = None
    cell_context: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_condition(condition: str) -> str | None:
    """Map common study vocabulary to a controlled cardiac label."""
    text = condition.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "sham": "reference", "control": "reference", "ctl": "reference",
        "healthy": "reference", "normal": "reference",
        "mi": "myocardial_injury", "myocardial_infarction": "myocardial_injury",
        "infarct": "myocardial_injury", "ischemia": "myocardial_injury",
        "i_r": "ischemia_reperfusion", "ischemia_reperfusion": "ischemia_reperfusion",
        "inflammation": "inflammatory", "inflammatory": "inflammatory",
        "hypertrophy": "hypertrophic", "fibrosis": "fibrotic",
        "metabolic": "metabolic", "arrhythmia": "electrophysiologic",
        "electrophysiology": "electrophysiologic",
        "pathogen": "pathogen_associated", "infection": "pathogen_associated",
    }
    return aliases.get(text)


def attach_normalized_label(record: SampleRecord) -> SampleRecord:
    label = normalize_condition(record.raw_condition)
    return SampleRecord(**{**record.to_dict(), "normalized_label": label})
