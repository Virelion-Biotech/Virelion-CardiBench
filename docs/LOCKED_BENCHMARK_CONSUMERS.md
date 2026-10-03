# Locked benchmark consumer contract (CardiLearn / CardiEval)

Locked manifests in `benchmarks/materialized/*.json` are the source of truth for splits.

## Required fields

- `benchmark_id`, `version`, `policy`, `seed`, `assignments`, `metadata_sha256`
- `label_counts`, `sample_count`, `group_count`
- optional `small_n_warning`

## Rules for trainers (CardiLearn)

1. Read assignments; never invent new splits for a locked benchmark_id+version.
2. Group by `group_id` from reconciled tables; do not split cells across train/val/test within a group.
3. If `small_n_warning` is set, report it in run metadata and prefer LOO or external validation.
4. Record `metadata_sha256` in every training run artifact.

## Rules for evaluators (CardiEval)

1. Verify `metadata_sha256` matches the locked file before scoring.
2. Reject runs whose train set intersects held-out groups.
3. Prefer metrics listed in the family catalog (`cardibench list-benchmarks`).

## Cross-study

Cross-study locked sets require each constituent study to be at `library_level_locked` (or higher) with compatible labels (`myocardial_injury` / `reference`).
