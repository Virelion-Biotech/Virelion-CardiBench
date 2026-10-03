# Virelion-CardiBench

CardiBench is the benchmark and dataset-intelligence layer for cardiac machine-learning evaluation in the Virelion HeartTwin stack. It combines leakage-aware benchmark construction with conservative public-evidence discovery, search, and protocol-scoped result history. It defines benchmark manifests, biological grouping rules, leakage checks, and reproducible benchmark artifacts.

## What it contains

- Metadata-first dataset and sample registries.
- Cardiac phenotype and condition normalization.
- Biological subject/donor/animal and technical-replicate grouping.
- Study, species, temporal, cell-context, and region split policies.
- Leakage validation and benchmark-readiness checks.
- Deterministic benchmark manifests and materialized assignments.
- Provenance hashes and reproducible benchmark artifacts.
- Benchmark definitions for cardiac-state, injury, transfer, temporal, multimodal, and challenge evaluation.
- CLI validation and repository audit commands.

CardiBench does not redistribute source datasets.

## Installation

```bash
pip install -e '.[test]'
pytest -q
```

## Usage

```bash
cardibench validate-manifest benchmarks/manifests/mi-vs-reference.v1.json
cardibench validate-all-manifests
cardibench list-benchmarks --json
cardibench audit --strict .
```

## Inputs and outputs

**Inputs:** dataset/sample metadata, benchmark manifests, biological grouping metadata, split policies, and benchmark definitions.

**Outputs:** validated benchmark manifests, deterministic split assignments, materialized benchmark artifacts, provenance hashes, readiness/audit reports, and benchmark metadata.

Preferred split hierarchy is biological subject, donor/animal, study for study-held-out tasks, and other required biological contexts. Technical replicates must not cross partitions.

## Validation

Validation checks schema and manifest integrity, grouping rules, leakage, duplicate or incompatible assignments, and benchmark readiness. Materialized benchmarks record benchmark identity, policy, seed, metadata, and a canonical SHA-256 digest.

Passing benchmark validation does not establish that a dataset is biologically representative or clinically generalizable.

## Limitations

Benchmark quality depends on the completeness and correctness of source metadata. Sample-level splitting may be unavoidable when stronger grouping metadata are unavailable and can overestimate generalization. Benchmark construction cannot remove biological confounding or study-specific bias.

## License

GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later). See `LICENSE`.


## Living intelligence and HeartTwin integration

CardiBench now exposes `benchmark.health`, `benchmark.search`, `benchmark.catalog`, `benchmark.discover`, `benchmark.result.record`, and `benchmark.results` alongside `benchmark.resolve`. Discovery observations are candidates only: they do not bypass dataset admission, reconciliation, biological grouping, readiness, or leakage checks. HeartTwin remains the orchestrator; CardiBridge owns transport; CardiTrace owns lineage; CardiEval owns independent scoring; CardiAtlas owns biomedical knowledge context.

The intended loop is `discover → reconcile/admit → benchmark.resolve → CardiLearn → CardiEval → benchmark.result.record → CardiTrace`. Search rankings are lexical retrieval signals, never quality or clinical-validity scores. See `docs/INTELLIGENCE_ARCHITECTURE.md`.


## Intelligence release, dashboard, and agent surface

The living intelligence layer can emit a deterministic release descriptor and a dependency-free read-only dashboard from the same catalog/result stores:

```bash
cardibench intelligence-report --json
cardibench release-intelligence
cardibench build-dashboard
```

The repository also includes `skills/cardibench-intelligence/SKILL.md` for HeartTwin-native agent use. It deliberately routes agents through HeartTwin's `benchmark.*` capabilities rather than turning CardiBench or CardiAgent into a second orchestrator.


## Fail-closed candidate admission

`benchmark.admission.assess` and `cardibench assess-admission` validate whether candidate metadata are sufficient for a leakage-checked materialization preview. The assessment never auto-admits a dataset: `ready_for_review` means only that required metadata are explicit and the preview satisfies software gates. Missing biological grouping or policy-specific metadata blocks admission rather than being inferred.
