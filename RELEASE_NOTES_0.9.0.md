# Virelion-CardiBench 0.9.0 — first locked MI-vs-reference library units

## Highlights

- **GSE153480** (Wang et al. Cell Reports 2020): litter-pool experimental units locked (pool / P1 / P8).
- **GSE106472**: WT MI vs WT No-MI locked; IRF3KO held out of primary binary.
- **GSE216211**: Sham vs MI locked; MI-E excluded by design.
- **GSE135310**: eligible single-timepoint libraries locked; multiplexed CITE-seq samples quarantined.
- **GSE219117 / GSE269054**: metadata-verified candidates (spatial / multi-genotype deferred).

## Tooling

- `cardibench materialize-from-table` — lock benchmarks from reconciled JSON tables.
- Materialized benchmarks emit `small_n_warning` when group count < 6.
- Leakage reports under `benchmarks/leakage/`.
- CI: pytest + manifest validation + audit + digest presence checks.

## Policy

- No individual animal IDs invented when GEO/paper only document pools.
- Expression matrices are **not** redistributed.
- Experimental unit = library/pool unless recoverable subject IDs exist.

## Digests

| Benchmark | SHA-256 |
|-----------|---------|
| gse153480-pool | 6c6f9b8d6dd679704bbbaa009ec1ba47760628f96815ceb4730abe999751bf8a |
| gse153480-P1 | 7594997ddb6ad55c44fb3c8e4e0bce55cb210d8f4ccd23d307e61109eef8e0f3 |
| gse153480-P8 | 04ab3925ba5ed978a9e25b5f9e35cdf96ee8aba11ce148627977d8d41f4c7487 |
| gse106472-wt | fbcbc6c7105b30c1559dad8354119fee807b197d5b0462350dc3e69a77693e48 |
| gse216211 | 2195a9baf4bff89c5f9a59c9e639c5efb553dd5e5cb99ea079878059c97d4566 |
| gse135310-eligible | 7d81e2d2491894cd54fd3b899b59a4fd7fe00af8dcbf94a7d5d1026152d6c73f |
