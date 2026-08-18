# Virelion-CardiBench

**A versioned benchmark and dataset registry for cardiac AI evaluation.**

CardiBench is the data/evaluation layer in the Virelion cardiac AI series. It does not generate biological challenges and it does not perform detection. Its purpose is to make evaluation datasets explicit, reproducible, versioned, and difficult to accidentally leak between training and testing.

## End-to-end workflow

```text
public study metadata
        |
        v
   GEO / dataset adapter
        |
        v
 normalized SampleRecord
        |
        +--> cardiac phenotype ontology
        |
        +--> quality + readiness gates
        |
        v
 benchmark policy selection
        |
        v
 leakage-aware materialization
        |
        +--> provenance / canonical hash
        |
        v
 reproducible locked benchmark
        |
        +-------------------+
        |                   |
        v                   v
    CardiLearn          CardiVex
        |                   |
        +---------+---------+
                  v
              CardiEval
```

## What is implemented

- Metadata-first dataset registry with accession, organism, tissue, modality, study and intended use.
- GEO-style sample metadata adapter with conservative condition normalization; ambiguous labels are rejected rather than guessed.
- Controlled cardiac phenotype ontology for reference, myocardial injury, ischemia-reperfusion, remodeling, inflammatory, hypertrophic, metabolic, electrophysiologic, fibrotic, cell-state and pathogen-associated phenotypes.
- Biological subject/donor/animal and technical-replicate grouping plus species, timepoint, cell-context and region metadata.
- Leakage-aware split generation and explicit subject, study, species, temporal, cell-context and region policies.
- Policy-specific leakage validation, not just generic subject leakage detection.
- Benchmark manifests with private-test and quality-gate declarations.
- Materialized benchmark objects with deterministic assignments, seed preservation and provenance hashes.
- Dataset quality and benchmark readiness gates.
- Benchmark family catalog covering cardiac-state classification, MI/reference, cell-context transfer, temporal generalization, cross-study generalization, cross-species transfer, multimodal prediction, pathogen-associated cardiac states and CardiVex blind challenge evaluation.
- Installable `cardibench` CLI with single-manifest validation, bulk manifest validation, benchmark listing and strict repository audit.
- End-to-end metadata fixtures and automated CI/package checks.

## Benchmark families

| Benchmark | Question |
|---|---|
| `cardiac-state-classification` | Can a model distinguish broad cardiac cellular states? |
| `mi-vs-reference` | Can a model distinguish myocardial-injury tissue from reference? |
| `cell-context-transfer` | Does a model generalize across cardiac cell contexts? |
| `study-heldout-generalization` | Does performance survive a completely held-out study? |
| `cross-species-transfer` | Does a learned phenotype transfer between species? |
| `temporal-injury-state` | Does the model generalize across injury phases? |
| `multimodal-cardiac-state` | Does a representation transfer across compatible cardiac modalities? |
| `pathogen-associated-cardiac-state` | Can pathogen-associated cardiac response states be distinguished from non-infectious injury/inflammation? |
| `cardivex-challenge-evaluation` | Can CardiVex detect blinded phenotype-level challenge cases? |

## Dataset registry

The registry is metadata-first and does not redistribute source data. A public-accession entry is not automatically a benchmark: it must pass provenance, condition-label, biological-grouping and leakage checks before promotion into a locked split.

A verified MI-focused evidence file currently records public GEO metadata for **GSE153480**, **GSE135310**, **GSE216211**, **GSE269054**, and the multimodal SuperSeries **GSE219117**. These entries are verified at the accession/series metadata level; exact animal/donor replicate mappings still have to be recovered before a locked benchmark is materialized.

## Leakage policy

CardiBench treats leakage as a benchmark failure, not merely a modeling issue. Preferred split hierarchy:

1. biological subject separation;
2. donor/animal separation;
3. study-level separation for cross-study tests;
4. explicit species/timepoint/cell-context/region separation when those define the benchmark;
5. sample-level splitting only when stronger grouping metadata are genuinely unavailable, with an explicit warning.

Technical replicates never cross partitions.

## Provenance and reproducibility

Materialized benchmarks carry dataset identifiers, benchmark policy, random seed, manifest metadata and a canonical SHA-256 digest. Equivalent metadata with different key ordering produce the same digest.

Benchmark result records also carry benchmark/model provenance so scores cannot be reported without identifying the evaluation artifact that produced them.

## CLI

```bash
pip install -e '.[test]'
pytest -q

cardibench validate-manifest benchmarks/manifests/mi-vs-reference.v1.json
cardibench validate-all-manifests
cardibench list-benchmarks --json
cardibench audit --strict .
```

## CI

The main workflow runs the tests, compilation, full benchmark-manifest validation and strict repository audit across Python 3.10–3.13, plus a separate wheel-build/install check. The repository deliberately distinguishes **code completeness** from **release verification**: a release is not declared fully verified until CI has produced a green run on the exact release commit.

## Safety boundary

CardiBench may represent pathogen-associated cardiac phenotypes and clinical observations, but benchmark metadata do not contain pathogen engineering parameters, propagation instructions, inoculation procedures, doses, or other operational biological instructions.

## Release status

**Release candidate.** The engineering workflow is complete enough for integration with CardiLearn/CardiVex. Final release verification still requires a successful GitHub Actions run on the exact `main` release commit and promotion of specific public datasets only after their sample-level biological replicate metadata have been reconciled.
