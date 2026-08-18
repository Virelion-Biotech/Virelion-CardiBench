# CardiBench integration contract

CardiBench owns benchmark definition, sample grouping, split policy, provenance and evaluation-artifact identity. It does not own model training or challenge generation.

## Upstream from real data

`SampleRecord` and the normalized registry provide model-ready metadata without redistributing source datasets.

## Downstream to CardiLearn

A materialized benchmark exposes:

- benchmark ID/version
- eligible sample IDs
- training/validation/test assignments
- normalized labels where permitted
- group policy
- seed
- provenance hash

The locked test labels are not part of public prediction input.

## Downstream to CardiVex

The `cardivex-challenge-evaluation` family accepts phenotype-level challenge cases produced by CardiAgent. CardiBench evaluates the resulting detection/characterization records without replacing CardiVex's detector.

## Result handoff

A benchmark result should identify:

- benchmark ID/version
- model ID/version
- split (`validation` or `test`)
- metric dictionary
- evaluated sample count
- benchmark provenance SHA-256

This makes results comparable across CardiLearn/CardiVex releases and prevents unscoped performance claims.
