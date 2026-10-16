# Data-preparation scripts

- `prepare_dataset.py` builds the eligible day-63 cohort, assessment counts, and VLE summaries from the seven OULAD source tables.
- `check_dataset.py` checks the versioned cohort table and writes `outputs/day63_dataset_check.json`.
- `inspect_oulad.py` summarizes source-table and processed-table quality in `outputs/step4_data_quality_report.md`.

See [`data/processed/README.md`](../data/processed/README.md) for setup, cohort rules, and the commands to rebuild the data. Set `EDUAI_RAW_DIR` only if the seven source CSVs are stored outside `data/raw/`.
