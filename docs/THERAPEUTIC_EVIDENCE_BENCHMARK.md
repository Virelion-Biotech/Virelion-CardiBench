# Cardiac Therapeutics Evidence Benchmark v1

## Scope

This is a **curation-first evidence registry**, not a treatment leaderboard, meta-analysis, clinical decision tool, or claim that candidate products regenerate myocardium. It complements CardiAtlas (biomedical evidence records), CardiEval (domain-separated interpretation), and CardiTrace (lineage/provenance). It does not replace the existing sample-level CardiBench leakage-aware ML benchmark.

## Four non-interchangeable strata

1. `myocardial_regeneration`: evidence of new cardiomyocyte generation and lineage/number, with maturation and integration separately recorded.
2. `myocardial_repair_preservation`: scar, remodelling, function, survival, cytoprotection or repair without presuming new myocardium.
3. `genetic_disease_modification`: correction or modification of a causal genetic/disease mechanism; not automatically regeneration.
4. `vascular_tissue_engineering`: vascular graft/tissue performance; not myocardial regeneration.

Zebrafish, mouse, organoid, engineered tissue, large-animal and human clinical studies are not pooled together. Different endpoints, assay definitions, timepoints, follow-up horizons and biological units are not pooled. The initial manifest is intentionally empty: candidate arms are discovery leads, not admitted evidence.

## Admission contract

A record is admitted only after manual primary-source adjudication. Required fields include study and study-family identifiers, biological unit and explicit denominator, intervention/comparator, species/model, dose/route/timing, endpoint and operational definition, assay, timepoint, effect estimate and uncertainty (including explicit `not_reported` states), adverse-event ascertainment, risk-of-bias assessment, analysis population, design fields, primary source identifier/URL and SHA-256 of the captured source artifact.

The hash must be computed from the locally archived source file by the curator; CardiBench does not fetch remote content or pretend a URL is a source hash. Do not hash an abstract and label it a full-text hash. Preserve the artifact type and access date in curator notes or the source archive manifest.

Missing denominator, comparator, endpoint definition, primary source, source hash or adjudication status blocks admission. Missing reported values must be explicitly encoded as unknown/not reported; they are never imputed as zero. The schema's permissive nested objects preserve source-specific uncertainty while the Python validator enforces required top-level gates.

Study-family leakage: one study family cannot silently appear in multiple strata. If a single paper contains genuinely distinct cohorts/experiments, curator must document the split and assign separate family IDs only with justification in source notes. Duplicate record IDs are rejected.

## Commands

```bash
cardibench validate-therapeutic-benchmark benchmarks/therapeutic_evidence/cardiac_therapeutics.v1.json
cardibench therapeutic-benchmark-summary benchmarks/therapeutic_evidence/cardiac_therapeutics.v1.json
```

Validation returns metadata and counts only. The summary is stratum-specific and emits no cross-stratum effect estimate or winner.

## Reproducible source inventory

`build_source_manifest(records)` emits a stable, sorted inventory with record IDs, study-family IDs, source identifiers, URLs and curator-supplied SHA-256 hashes. It does not download sources. Preserve the source archive separately under its applicable licence; CardiBench does not redistribute publications or datasets.

## Interpretation boundary

A benchmark record is not independent replication. A study-family count is not a participant count. A statistically significant functional endpoint does not establish regeneration. CardiEval's independent domains (cell-cycle entry, cytokinesis, lineage/number, maturation, function/remodelling, scar, arrhythmia safety, off-target toxicity) should be linked rather than collapsed into a single score. No cross-modality winner is calculated.
