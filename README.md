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
- Biological subject/donor/animal and technical-replicate grouping.
- Leakage-aware split generation and explicit study-held-out, species-held-out and temporal policies.
- Benchmark manifests with private-test and quality-gate declarations.
- Materialized benchmark objects with deterministic assignments and provenance hashes.
- Dataset quality and benchmark readiness gates.
- Benchmark family catalog covering core cardiac-state and generalization tasks.
- Installable `cardibench` CLI and automated tests/CI.

## Benchmark families

| Benchmark | Question |
|---|---|
| `cardiac-state-classification` | Can a model distinguish broad cardiac cellular states? |
| `mi-vs-reference` | Can a model distinguish myocardial-injury tissue from reference? |
| `remodeling-state` | Can a model identify remodeling-associated cellular programs? |
| `cell-context-transfer` | Does a model generalize across cardiac cell contexts? |
| `study-heldout-generalization` | Does performance survive a completely held-out study? |
| `cross-species-transfer` | Does a learned phenotype transfer between species? |
| `temporal-injury-generalization` | Does the model generalize across injury time? |
| `modality-transfer` | Does a representation transfer between compatible modalities? |
| `cardivex-challenge-evaluation` | Can CardiVex detect blinded phenotype-level challenge cases? |

## Dataset registry

The registry currently contains candidate public cardiac datasets and a higher-priority MI/sham candidate set, including human cardiac reference atlases, experimental mouse injury datasets, macrophage-focused MI datasets, and multimodal injury studies.

Registry entries are metadata-only references. CardiBench does not redistribute source datasets. Candidate entries requiring exact condition/sample verification remain marked as such until their source metadata have been reconciled.

## Leakage policy

CardiBench treats leakage as a benchmark failure, not merely a modeling issue. Preferred split hierarchy:

1. subject-level separation;
2. donor/animal-level separation;
3. study-level separation for cross-study tests;
4. technical replicate grouping;
5. sample-level splitting only when stronger grouping metadata are unavailable, with an explicit warning.

A benchmark must declare its split policy and grouping key. Technical replicates are never allowed to cross partitions.

## Provenance and reproducibility

Materialized benchmarks carry dataset identifiers, benchmark policy, random seed, manifest metadata, preprocessing/version metadata and a canonical metadata hash. Canonical hashing is key-order independent so equivalent metadata produce the same provenance identifier.

## Validation and CI

Install the package and run the test suite with:

```bash
pip install -e '.[test]'
pytest
```

Validate a JSON benchmark manifest with:

```bash
cardibench validate-manifest benchmarks/manifests/mi-vs-reference.v1.json
```

GitHub Actions runs the test suite and byte-compilation checks across supported Python versions.

## Safety boundary

CardiBench may represent pathogen-associated cardiac phenotypes and clinical observations, but benchmark metadata do not contain pathogen engineering parameters, propagation instructions, inoculation procedures, doses, or other operational biological instructions.

## Release status

CardiBench is considered release-ready when the repository audit passes, benchmark manifests validate, the test suite passes in CI, and all datasets used for a locked benchmark have verified provenance, labels and grouping metadata. The current branch contains the complete engineering workflow and remains open to expansion with additional verified public datasets and benchmark families.
