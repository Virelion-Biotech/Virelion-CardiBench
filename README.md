# Virelion-CardiBench

**A versioned benchmark and dataset registry for cardiac AI evaluation.**

CardiBench is the data/evaluation layer in the Virelion cardiac AI series. It does not generate biological challenges and it does not perform detection. Its purpose is to make evaluation datasets explicit, reproducible, versioned, and difficult to accidentally leak between training and testing.

## Role in the Virelion ecosystem

```text
CardiAtlas  -> evidence / literature / dataset provenance
     |
     v
CardiBench  -> curated benchmark definitions + locked splits
     |
     +------------------+
     |                  |
     v                  v
CardiLearn          CardiAgent
real-data models    phenotype challenges
     |                  |
     +--------+---------+
              v
          CardiVex
              |
              v
          CardiEval
```

## Design goals

- **Dataset provenance:** every dataset records its source, accession where applicable, species, tissue, assay, study, and processing status.
- **Leakage resistance:** split at the biological subject/study level where metadata permit; never split technical replicates across train/test.
- **Benchmark isolation:** benchmark definitions describe immutable cases and expected labels without embedding private test labels in public prediction inputs.
- **Multimodal support:** single-cell RNA-seq, single-nucleus RNA-seq, bulk RNA-seq, spatial transcriptomics, proteomics, imaging, electrophysiology, and phenotype tables can be represented through a common manifest.
- **Cardiac state coverage:** healthy/reference, ischemic injury, remodeling, inflammatory, hypertrophic, metabolic, electrophysiologic, fibrosis, cell-state, and pathogen-associated cardiac phenotypes can be represented without encoding operational biological instructions.
- **Reproducibility:** manifests, hashes, preprocessing versions, and split policies are first-class metadata.

## Repository structure

```text
benchmarks/       benchmark manifests
schemas/          JSON schemas for datasets, samples, labels, and splits
registry/         human-readable dataset registry
examples/         small metadata-only examples
tests/            schema and integrity tests
src/cardi_bench/  Python validation and manifest utilities
```

## Core objects

### DatasetRecord

Describes a source dataset and its provenance.

### SampleRecord

Describes a biological or technical sample, including subject/study grouping needed for leakage-aware splitting.

### BenchmarkDefinition

Defines the prediction task, eligible modalities, phenotype ontology, split policy, and evaluation target.

### SplitManifest

Materializes train/validation/test membership while preserving subject/study grouping.

## Example benchmark families

| Benchmark | Question |
|---|---|
| `cardiac-state-classification` | Can a model distinguish broad cardiac cellular states? |
| `mi-vs-reference` | Can a model distinguish myocardial-injury tissue from matched reference? |
| `remodeling-state` | Can a model identify remodeling-associated cellular programs? |
| `cell-context-transfer` | Does a model generalize across cardiac cell contexts? |
| `study-heldout-generalization` | Does performance survive a completely held-out study? |
| `modality-transfer` | Does a representation transfer between compatible modalities? |
| `cardivex-challenge-evaluation` | Can CardiVex detect blinded phenotype-level challenge cases? |

The registry is deliberately metadata-first. A benchmark entry can point to a public accession or externally hosted dataset without redistributing the underlying data.

## Leakage policy

CardiBench treats leakage as a benchmark failure, not merely a modeling issue. Preferred split hierarchy:

1. subject-level separation;
2. donor/animal-level separation;
3. study-level separation for cross-study tests;
4. technical replicate grouping;
5. sample-level splitting only when stronger grouping metadata are unavailable, with an explicit warning.

A benchmark must declare its split policy and grouping key.

## Safety boundary

CardiBench may represent pathogen-associated cardiac phenotypes and clinical observations, but benchmark metadata do not contain pathogen engineering parameters, propagation instructions, inoculation procedures, doses, or other operational biological instructions.

## Status

The repository is the foundation for the benchmark registry. Dataset-specific entries should be added only after provenance, metadata quality, label definition, and leakage controls are documented.
