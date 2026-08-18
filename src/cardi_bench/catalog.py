"""Curated benchmark-family catalog and task requirements."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class BenchmarkFamily:
    benchmark_id: str
    task: str
    description: str
    preferred_group_key: str
    required_modalities: tuple[str, ...]
    primary_metrics: tuple[str, ...]

BENCHMARK_FAMILIES = (
    BenchmarkFamily("mi-vs-reference", "binary_classification", "Distinguish myocardial injury from matched reference tissue.", "biological_subject", ("single-cell RNA-seq", "single-nucleus RNA-seq"), ("auroc", "auprc", "balanced_accuracy", "sensitivity", "specificity")),
    BenchmarkFamily("study-heldout-generalization", "cross-study_generalization", "Test phenotype recognition on a completely held-out study.", "study", ("single-cell RNA-seq", "single-nucleus RNA-seq", "spatial transcriptomics"), ("auroc", "auprc", "macro_f1", "calibration")),
    BenchmarkFamily("cell-context-transfer", "cell-context_transfer", "Train in selected cardiac cell contexts and test on unseen compatible contexts.", "biological_subject", ("single-cell RNA-seq", "single-nucleus RNA-seq"), ("macro_f1", "balanced_accuracy", "calibration")),
    BenchmarkFamily("temporal-injury-state", "temporal_generalization", "Train on selected timepoints and evaluate at held-out injury phases.", "biological_subject", ("single-cell RNA-seq", "single-nucleus RNA-seq", "spatial transcriptomics"), ("macro_f1", "auroc", "auprc")),
    BenchmarkFamily("cross-species-transfer", "species_transfer", "Evaluate whether cardiac phenotype representations transfer between mammalian species.", "biological_subject", ("single-cell RNA-seq", "single-nucleus RNA-seq"), ("macro_f1", "balanced_accuracy", "calibration")),
    BenchmarkFamily("multimodal-cardiac-state", "multimodal_classification", "Evaluate compatible representations across transcriptomic, spatial and phenotype measurements.", "biological_subject", ("single-nucleus RNA-seq", "spatial transcriptomics", "phenotype table"), ("auroc", "auprc", "macro_f1")),
    BenchmarkFamily("pathogen-associated-cardiac-state", "phenotype_classification", "Distinguish pathogen-associated cardiac response states from non-infectious inflammatory or injury phenotypes.", "biological_subject", ("single-cell RNA-seq", "single-nucleus RNA-seq", "clinical phenotype"), ("macro_f1", "auprc", "calibration")),
    BenchmarkFamily("cardivex-challenge-evaluation", "blind_detection", "Measure CardiVex detection and characterization performance on blinded CardiAgent cases.", "challenge_case", ("phenotype-level challenge",), ("detection_rate", "characterization_accuracy", "calibration")),
)

def get_benchmark_family(benchmark_id: str) -> BenchmarkFamily:
    for family in BENCHMARK_FAMILIES:
        if family.benchmark_id == benchmark_id:
            return family
    raise KeyError(f"Unknown benchmark family: {benchmark_id}")
