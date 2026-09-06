# Virelion-CardiBench

CardiBench is a benchmark registry and dataset-management library for cardiac machine-learning evaluation. It defines benchmark manifests, biological grouping rules, leakage checks, and reproducible benchmark artifacts.

## Scope

CardiBench provides:

- metadata-first dataset and sample registries;
- cardiac phenotype and condition normalization;
- biological subject/donor/animal and technical-replicate grouping;
- study, species, temporal, cell-context, and region split policies;
- leakage validation and benchmark readiness checks;
- deterministic benchmark manifests and materialized assignments;
- provenance hashes and reproducible benchmark artifacts;
- benchmark-family definitions for cardiac-state, injury, transfer, temporal, multimodal, and challenge evaluation;
- CLI validation and repository audit commands.

CardiBench does not redistribute source datasets. A public accession is not automatically a benchmark; it must satisfy the relevant metadata and leakage requirements.

## Benchmark workflow

```text
source metadata
      ↓
SampleRecord
      ↓
metadata / grouping QC
      ↓
benchmark policy
      ↓
leakage validation
      ↓
locked manifest
      ↓
materialized benchmark
      ↓
CardiEval
```

## Benchmark families

| ID | Purpose |
|---|---|
| `cardiac-state-classification` | cardiac cellular-state classification |
| `mi-vs-reference` | myocardial injury vs reference |
| `cell-context-transfer` | transfer across cardiac cell contexts |
| `study-heldout-generalization` | held-out study generalization |
| `cross-species-transfer` | cross-species transfer |
| `temporal-injury-state` | injury-phase generalization |
| `multimodal-cardiac-state` | multimodal representation transfer |
| `pathogen-associated-cardiac-state` | pathogen-associated host-response states |
| `cardivex-challenge-evaluation` | CardiVex challenge evaluation |

## Leakage policy

Preferred separation hierarchy:

1. biological subject;
2. donor/animal;
3. study for study-held-out tasks;
4. species, timepoint, cell context, or region where required by the benchmark;
5. sample-level splitting only when stronger grouping metadata are unavailable and the limitation is recorded.

Technical replicates must not cross partitions.

## Installation

```bash
pip install -e '.[test]'
pytest -q
```

## CLI

```bash
cardibench validate-manifest benchmarks/manifests/mi-vs-reference.v1.json
cardibench validate-all-manifests
cardibench list-benchmarks --json
cardibench audit --strict .
```

## Integration

CardiBench produces benchmark packages consumed by CardiEval. CardiAtlas can supply biological metadata and provenance context. CardiLearn and CardiVex can consume benchmark definitions without owning benchmark split policy.

## Reproducibility

Materialized benchmarks record benchmark identity, policy, random seed, manifest metadata, and a canonical SHA-256 digest. Benchmark results should identify the exact benchmark artifact used for evaluation.

## Limitations

Benchmark readiness is a data-quality property, not evidence that a dataset is biologically representative or that a model will generalize clinically. Metadata gaps, subject mapping, study-family independence, and phenotype interpretation require scientific review.

## License

GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later). See `LICENSE`.

## Citation

Cite the specific CardiBench release and the original source datasets/publications used in a benchmark.
