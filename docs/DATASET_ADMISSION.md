# CardiBench dataset admission

A dataset enters the registry as a **candidate**. It becomes benchmark-eligible only after the metadata required for the intended task can be verified.

## Admission gates

1. **Provenance** — public accession/source, organism, tissue, modality, and study identity are recorded.
2. **Label provenance** — the condition is supported by the source metadata; CardiBench never infers an unverified disease label from a sample name alone.
3. **Biological grouping** — donor/animal/subject identity is captured when available.
4. **Replicate grouping** — technical libraries/replicates remain attached to their biological source.
5. **Task compatibility** — modality, tissue, cell context, region, and timepoint satisfy the benchmark definition.
6. **Leakage safety** — the proposed split produces no biological-group or technical-replicate overlap.
7. **Reproducibility** — the materialized split receives a deterministic metadata digest.

## Statuses

- `candidate`: discovered and registered; not safe to use automatically.
- `metadata_verified`: provenance and label metadata checked.
- `benchmark_ready`: passes the benchmark-specific quality/readiness gates.
- `locked`: a benchmark split has been materialized and its manifest digest recorded.

## Ambiguity rule

When metadata contains conflicting condition cues (for example, both injury and reference terms), the adapter returns `ambiguous` and rejects the sample from automatic benchmark construction. Human review is required.

## Source-data policy

CardiBench stores metadata and reproducibility descriptors. It does not redistribute restricted source datasets. Benchmark manifests point to public accessions or externally managed data locations.
