# CardiBench release checklist

A release is complete when the following are true:

- [ ] Dataset registry entries have explicit provenance and status.
- [ ] Source adapters reject ambiguous condition metadata.
- [ ] Normalized sample schema and ontology are versioned.
- [ ] Quality gates reject duplicates, unresolved labels, and leakage.
- [ ] Every benchmark family has a machine-readable manifest.
- [ ] Split policies are deterministic and biological-group aware.
- [ ] Materialized benchmarks carry a deterministic SHA-256 digest.
- [ ] Locked test labels are not part of public prediction input.
- [ ] Benchmark result records carry model and benchmark provenance.
- [ ] End-to-end fixtures exercise adapter → normalization → quality → split.
- [ ] CLI validates representative manifests and can audit the repository.
- [ ] CI runs tests, compilation, manifest validation, and package builds.
- [ ] Final CI run is green on the exact release commit.

The final CI condition is intentionally separate from code completeness: a
repository should not be called release-verified merely because the workflows
exist.
