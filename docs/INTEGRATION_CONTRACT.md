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


## Living intelligence control plane

CardiBench also owns benchmark/dataset discovery, conservative evidence identity, local search, and protocol-scoped result history. These are control-plane capabilities and do not become patient/subject `CardiacState` observations. HeartTwin should invoke them through `benchmark.*` capabilities, while only `benchmark.resolve` is reduced into canonical subject state.

Canonical evaluation loop:

```text
CardiBench benchmark.resolve → CardiLearn → CardiEval → CardiBench benchmark.result.record → CardiTrace
```

`benchmark.result.record` preserves the benchmark fingerprint, split, protocol identity, model identity and metric observations. Results with different comparability keys are not silently pooled.

CardiBridge may transport `benchmark.evidence` and `benchmark.result`; CardiTrace remains the source of execution/artifact lineage. CardiAtlas identifiers may be retained as evidence, but CardiBench must not invent Atlas entities from ambiguous source metadata.
