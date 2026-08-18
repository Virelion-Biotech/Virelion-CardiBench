"""CardiBench: reproducible cardiac benchmark infrastructure."""

from .adapters import AdapterResult, adapt_geo_samples
from .catalog import BENCHMARK_FAMILIES, BenchmarkFamily, get_benchmark_family
from .manifest import assert_valid_manifest, validate_manifest
from .ontology import CELL_CONTEXTS, LABELS, MODALITIES, REGIONS, canonical_label
from .provenance import ProvenanceRecord, canonical_metadata_hash, make_provenance
from .quality import QualityReport, assess_dataset
from .registry import Sample, summarize_samples, validate_no_group_leakage
from .samples import SampleRecord, attach_normalized_label, normalize_condition
from .splits import make_group_split, split_summary
from .splitting import group_key, make_grouped_split, split_statistics

__all__ = [
    "Sample", "SampleRecord", "AdapterResult", "adapt_geo_samples",
    "normalize_condition", "attach_normalized_label", "canonical_label",
    "validate_no_group_leakage", "summarize_samples", "group_key",
    "make_grouped_split", "split_summary", "split_statistics",
    "QualityReport", "assess_dataset", "LABELS", "CELL_CONTEXTS", "REGIONS", "MODALITIES",
    "validate_manifest", "assert_valid_manifest",
    "BenchmarkFamily", "BENCHMARK_FAMILIES", "get_benchmark_family",
    "ProvenanceRecord", "canonical_metadata_hash", "make_provenance",
]
