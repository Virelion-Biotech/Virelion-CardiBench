# CardiBench living intelligence architecture

## Design goal

Add living benchmark discovery/catalog/search/history without turning CardiBench into a parallel HeartTwin or a second CardiAtlas.

```text
public sources → CardiBench observations → identity resolution → searchable catalog
→ dataset admission/reconciliation/readiness → benchmark.resolve
→ HeartTwin → CardiLearn → CardiEval → benchmark.result.record → CardiTrace
```

### Boundaries

A source observation is immutable evidence that a source exposed a record; scheduled refreshes write append-only timestamp/run-qualified snapshot files so same-day reruns cannot overwrite evidence; it is not an admitted dataset. A catalog record is searchable normalized evidence. The existing registry remains the gate for biological metadata, subject grouping, labels, replicates and eligibility. Benchmark manifests remain deterministic and leakage checked. Result observations preserve one concrete evaluation under one benchmark fingerprint/protocol and are never pooled across incompatible comparability keys.

Search reports matched/missing tokens, fields, lexical coverage and retrieval score. The score is query-local retrieval evidence, not scientific quality or clinical validity.

Each source reports health independently. A connector must emit `SourceObservation`, preserve identity/URI, avoid inferring missing biology, use bounded calls, expose failures, and not require changing HeartTwin/CardiTrace ownership.

Global discovery/search remains control-plane state. Only a resolved benchmark used by a workflow enters canonical `CardiacState`.
