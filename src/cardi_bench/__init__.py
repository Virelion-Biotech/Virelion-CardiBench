"""CardiBench: reproducible cardiac benchmark infrastructure."""

from .adapters import AdapterResult, adapt_geo_samples
from .manifest import assert_valid_manifest, validate_manifest
from .ontology import CELL_CONTEXTS, LABELS, MODALITIES, REGIONS, canonical_label
from .registry import Sample, summarize_samples, validate_no_group_leakage
from .samples import SampleRecord, attach_normalized_label, normalize_condition
from .splits import make_group_split, split_summary
from .splitting import group_key, make_grouped_split, split_statistics

__all__ = [
    "Sample", "SampleRecord", "AdapterResult", "adapt_geo_samples",
    "normalize_condition", "attach_normalized_label", "canonical_label",
    "validate_no_group_leakage", "summarize_samples", "group_key",
    "make_grouped_split", "split_summary", "make_grouped_split",
    "split_statistics", "LABELS", "CELL_CONTEXTS", "REGIONS", "MODALITIES",
    "validate_manifest", "assert_valid_manifest",
]
