# Day-63 student risk dataset

This folder contains the prepared OULAD dataset: [student_risk_at_day_63.csv](student_risk_at_day_63.csv), with 26,292 eligible student-course records. It is a research prototype; no model has been trained, and it is not evidence about current students at our institution.

## Rebuild

Download the source CSVs from the [UCI OULAD record](https://archive.ics.uci.edu/dataset/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset) into `data/raw/`, then run from the repository root:

~~~powershell
python -m pip install -r requirements-data-prep.txt
python scripts\prepare_dataset.py
python scripts\check_dataset.py
~~~

The scripts write generated files to `outputs/`; the reviewed CSV in this folder is the versioned dataset.

## Notes

- [dataset_guide.md](dataset_guide.md): columns and joins.
- [how_risk_is_defined.md](how_risk_is_defined.md): label and cutoff rules.
- [data_quality_notes.md](data_quality_notes.md): data checks and preparation observations.

OULAD is listed as CC BY 4.0. Please cite Kuzilek, Hlosta, and Zdrahal (2017), [Open University Learning Analytics Dataset](https://doi.org/10.1038/sdata.2017.171), *Scientific Data*, 4, 170171.
