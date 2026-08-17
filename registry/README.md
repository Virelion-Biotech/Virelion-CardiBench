# Dataset registry

This directory records candidate datasets before they become benchmark inputs.

Each entry should document:

- accession/source;
- species and cardiac tissue;
- assay/modality;
- biological subjects/donors/animals;
- study identifiers;
- condition labels and their definitions;
- technical replicate structure;
- preprocessing status;
- license/access restrictions;
- intended benchmark role;
- known confounders;
- leakage risks.

Do not add a dataset to a benchmark solely because its accession exists. The benchmark maintainer should verify that the labels and biological grouping support the intended task.

## Initial registry targets

- public human cardiac single-cell and single-nucleus datasets;
- myocardial infarction versus reference/sham datasets;
- cardiac remodeling datasets;
- hypertrophy/failure datasets;
- inflammatory/myocarditis-associated datasets;
- cardiac maturation/development datasets;
- multimodal cardiac datasets where sample identity can be reconciled.

Pathogen-associated datasets may be represented when the public data support a legitimate cardiac phenotype task; entries should remain descriptive and provenance-focused.
