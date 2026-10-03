from cardi_bench import BENCHMARK_FAMILIES, canonical_metadata_hash, get_benchmark_family, make_provenance


def test_benchmark_catalog_contains_core_families():
    ids = {item.benchmark_id for item in BENCHMARK_FAMILIES}
    assert {"mi-vs-reference", "study-heldout-generalization", "cardivex-challenge-evaluation"} <= ids
    assert get_benchmark_family("mi-vs-reference").preferred_group_key == "biological_subject"


def test_canonical_metadata_hash_is_order_independent():
    a = {"sample": "x", "condition": "MI"}
    b = {"condition": "MI", "sample": "x"}
    assert canonical_metadata_hash(a) == canonical_metadata_hash(b)


def test_provenance_contains_metadata_hash():
    record = make_provenance(
        source="GEO",
        accession="GSE153480",
        registry_version="1.0",
        metadata={"sample": "GSM1"},
        preprocessing_version="raw-metadata-v1",
        manifest_version="mi-vs-reference-v1",
    )
    assert len(record.metadata_hash) == 64
