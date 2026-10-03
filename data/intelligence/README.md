# CardiBench intelligence products

- `snapshots/YYYYMMDDTHHMMSSZ-RUN_ID-ATTEMPT.json`: immutable discovery observations plus per-source health. A refresh never reuses a snapshot path.
- `catalog.json`: generated normalized catalog; rebuild it from snapshots.
- `results.json`: optional protocol-scoped benchmark result history.

Discovery evidence is not dataset admission or benchmark readiness.

Generated catalog/release/dashboard files are rebuildable products; timestamped source snapshots are append-only evidence.
