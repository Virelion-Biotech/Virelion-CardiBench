"""CardiBench: reproducible cardiac benchmark infrastructure."""

from .manifest import assert_valid_manifest, validate_manifest
from .registry import Sample, summarize_samples, validate_no_group_leakage
from .samples import SampleRecord, attach_normalized_label, normalize_condition
from .splitting import group_key, make_grouped_split, split_statistics

__all__ = [
    "Sample", "SampleRecord", "normalize_condition", "attach_normalized_label",
    "validate_no_group_leakage", "summarize_samples", "group_key",
    "make_grouped_split", "split_statistics", "validate_manifest", "assert_valid_manifest",
]
