# Intelligence release and dashboard

CardiBench can package its living catalog and protocol-scoped results into a deterministic release descriptor and a dependency-free static dashboard.

```bash
cardibench intelligence-report --json
cardibench release-intelligence
cardibench build-dashboard
```

The release descriptor fingerprints the normalized catalog and result history with canonical SHA-256 hashes. The dashboard consumes those same products; it is not a second database or service.

## Stack boundary

The dashboard and release bundle are control-plane products. They must never become biological observations in HeartTwin `CardiacState`. HeartTwin consumes CardiBench through `benchmark.*` capabilities, CardiEval produces independent scores, CardiBridge transports portable benchmark evidence/result contracts, and CardiTrace owns run/artifact lineage.

## Comparability

Result summaries preserve CardiBench comparability groups. They do not combine observations across differing benchmark fingerprints, splits, task protocols, or evaluator/source identities.
