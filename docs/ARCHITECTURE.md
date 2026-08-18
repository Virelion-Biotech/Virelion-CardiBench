# CardiBench architecture

```text
public study metadata
        |
        v
   dataset registry
        |
        v
    source adapter
        |
        v
 normalized samples
        |
        +--> cardiac ontology
        |
        +--> quality gates
        |
        +--> provenance
        |
        v
 benchmark family
        |
        v
   split policy
        |
        v
 materialization
        |
        +--> leakage check
        +--> label balance
        +--> deterministic digest
        |
        v
 locked benchmark
        |
   +----+-----------+
   |                |
   v                v
CardiLearn       CardiVex
   |                |
   +-------+--------+
           v
       CardiEval
```

CardiBench deliberately does not own model training or challenge generation. It provides stable, auditable inputs and task definitions for those downstream systems.

## Layers

### Registry
Human-readable dataset records with accession, species, tissue, modality, study design, intended use, and metadata quality status.

### Adapters
Convert source-specific metadata into normalized `SampleRecord`/`Sample` objects. Adapters return explicit ambiguity and rejection information rather than guessing.

### Ontology
Controls labels, modalities, anatomical regions, and cell contexts so equivalent study vocabulary maps to consistent benchmark concepts.

### Quality and readiness
Check labels, duplicate IDs, biological grouping, minimum cohort structure, and benchmark-specific gates.

### Policies and materialization
Turn verified samples into deterministic train/validation/test assignments using subject, study, species, or temporal boundaries. Biological and technical replicate leakage is treated as a benchmark failure.

### Provenance
Every materialized benchmark can be tied to source metadata, preprocessing/version information, and a canonical SHA-256 digest.

### Results
`BenchmarkResult` is the handoff contract for downstream evaluation systems. Results may only report validation or locked test performance and must carry provenance.
