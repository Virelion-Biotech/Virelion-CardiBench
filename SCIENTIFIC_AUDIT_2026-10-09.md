# Scientific audit changes — 2026-10-09

## Behavior

Add immutable declared dataset-lineage overlap checks, optional independence admission blockers and training-only transformer fitting with biological-unit separation.

## Scope and remaining evidence

Complete declarations are required for no-known-overlap status. Study/lab relationships and unreported pretraining cannot be inferred. Transformer persistence is the caller responsibility. Existing preprocessing paths are not automatically replaced; fit_transform_fold must be used before preprocessing.

## Implementation

- `src/cardi_bench/contamination.py`
- `tests/test_contamination.py`
- `src/cardi_bench/admission.py`

## Verification

Regression tests accompany the changes. Repository test results are recorded in the audit completion report and draft pull request. Software regression checks do not establish numerical, biological, transport or clinical validity.
