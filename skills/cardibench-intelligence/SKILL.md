# CardiBench Intelligence Skill

Use CardiBench intelligence only through the HeartTwin service surface. HeartTwin remains the orchestrator; CardiBench owns discovery/catalog/search/result history; CardiBridge owns transport; CardiTrace owns execution and artifact lineage.

## Capabilities

- `benchmark.health`: inspect available CardiBench capabilities and configured stores.
- `benchmark.search`: search normalized evidence. Retrieval scores are lexical signals, not quality scores.
- `benchmark.catalog`: list normalized evidence records with optional type/source filters.
- `benchmark.discover`: collect bounded public-source observations. A discovery observation is a candidate only.
- `benchmark.admission.assess`: fail-closed metadata/readiness assessment before scientific admission; returns `blocked` or `ready_for_review` and never auto-approves a dataset.
- `benchmark.resolve`: materialize an already admitted benchmark from supplied sample metadata and biological split constraints.
- `benchmark.result.record`: record a CardiEval result only after independent evaluation.
- `benchmark.results`: retrieve protocol-scoped result history.

## Required rules

1. Never treat discovery as dataset admission. Candidates must still pass reconciliation, biological grouping, readiness, and leakage checks.
2. Never infer missing donor, animal, subject, replicate, condition, or timepoint metadata.
3. Do not write discovery/catalog/search records into canonical HeartTwin `CardiacState`. Only a resolved benchmark used by a workflow belongs in subject state.
4. Never pool or rank results across different comparability keys. Benchmark fingerprint, split, protocol, and evaluator/source identity must match.
5. Route independent scoring to CardiEval, transport to CardiBridge, and execution/artifact lineage to CardiTrace.
6. Preserve unknown/unverified states instead of converting missing evidence to false or zero.
7. Do not make clinical-validity claims from catalog presence, retrieval rank, or benchmark scores.

## Preferred flow

`benchmark.health → benchmark.search/catalog → benchmark.admission.assess → scientific review/reconciliation → benchmark.resolve → CardiLearn → CardiEval → benchmark.result.record → CardiTrace`

For a HeartTwin-native caller, prefer `VirelionServices.benchmark_search`, `benchmark_catalog`, `benchmark_discover`, `benchmark_admission`, `benchmark`, `benchmark_record_result`, and `benchmark_results` rather than importing CardiBench directly.
