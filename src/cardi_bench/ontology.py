"""Controlled ontology for cardiac benchmark labels and contexts."""
from __future__ import annotations

LABELS = {
    "reference": "Reference/sham/healthy cardiac state",
    "myocardial_injury": "Myocardial injury / infarction-associated state",
    "ischemia_reperfusion": "Ischemia-reperfusion associated state",
    "inflammatory": "Inflammatory cardiac state",
    "remodeling": "Post-injury or chronic remodeling state",
    "fibrotic": "Fibrotic / extracellular-matrix remodeling state",
    "hypertrophic": "Hypertrophic cardiac state",
    "metabolic": "Metabolic stress/remodeling state",
    "electrophysiologic": "Electrical/electrophysiologic dysfunction state",
    "cell_state": "Altered cardiac cell-state phenotype",
    "pathogen_associated": "Pathogen-associated cardiac phenotype",
}

CELL_CONTEXTS = (
    "cardiomyocyte", "fibroblast", "endothelial", "immune",
    "pericyte", "smooth_muscle", "multicellular_cardiac_context",
)

REGIONS = (
    "whole_heart", "infarct", "infarct_border_zone", "remote_zone",
    "left_ventricle", "right_ventricle", "septum", "apex", "atrium",
)

MODALITIES = (
    "scRNA-seq", "snRNA-seq", "bulk RNA-seq", "spatial transcriptomics",
    "proteomics", "imaging", "electrophysiology", "clinical", "multimodal",
)


def canonical_label(label: str) -> str | None:
    value = (label or "").strip().lower().replace(" ", "_")
    aliases = {
        "sham": "reference", "control": "reference", "healthy": "reference",
        "mi": "myocardial_injury", "infarct": "myocardial_injury",
        "ischemia": "myocardial_injury", "i_r": "ischemia_reperfusion",
        "fibrosis": "fibrotic", "infection": "pathogen_associated",
        "viral": "pathogen_associated", "bacterial": "pathogen_associated",
    }
    if value in LABELS:
        return value
    return aliases.get(value)
