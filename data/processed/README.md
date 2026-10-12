# OULAD day-63 data preparation

This folder contains the reviewed day-63 dataset and notes describing how it was prepared.

## Versioned dataset

`student_risk_at_day_63.csv` contains 26,292 eligible student-course records. It includes the binary `at_risk` target and a precomputed student-disjoint evaluation assignment (`train`, `test`, or `excluded_overlap`). The source `final_result` and `id_student` columns are omitted. Demographic fields are retained only for subgroup checks; `evaluation_split` and cutoff fields are metadata, not predictors.

## Rebuild

Download the OULAD source CSVs from the [UCI dataset record](https://archive.ics.uci.edu/dataset/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset) and place them under `data/raw/`. Raw source CSVs and other generated CSVs are ignored by Git. From the repository root, run:

```powershell
python -m pip install -r requirements-data-prep.txt
python scripts\prepare_dataset.py
python scripts\check_dataset.py
```

The UCI record lists OULAD under CC BY 4.0. This derived table adapts OULAD through linked-table joins, day-63 feature filtering, cohort filtering, target mapping, and evaluation-split assignment. Cite Kuzilek, Hlosta, and Zdrahal (2017), *Open University Learning Analytics Dataset*, *Scientific Data*, 4, 170171, https://doi.org/10.1038/sdata.2017.171.

## Supporting notes

- `dataset_guide.md` describes joins, feature meanings, target, split, and limitations.
- `how_risk_is_defined.md` records label, cutoff, and leakage rules.
- `data_quality_notes.md` records the source and modelling-table inspection.
- `week_one_checklist.md` maps the work to the Week 1 checklist.

No model has been trained. This public dataset supports a prototype and should not be interpreted as evidence about current students at the project institution.
