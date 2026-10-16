# Processed OULAD data

`student_risk_at_day_63.csv` is the de-identified cohort table prepared from OULAD. It contains 26,422 eligible student-course records and 40 columns. It includes the retrospective `at_risk` label, but no student ID, final-result text, unregistration date, or train/test assignment.

## Rebuild

Download OULAD from the [UCI dataset record](https://archive.ics.uci.edu/dataset/349/open%2Buniversity%2Blearning%2Banalytics%2Bdataset), place its seven source CSV files in `data/raw/`, and run from the repository root:

```powershell
python -m pip install -r requirements-data-prep.txt
python scripts\prepare_dataset.py
python scripts\check_dataset.py
python scripts\inspect_oulad.py
```

The preparation script builds the day-63 cohort and cutoff-based assessment and VLE summaries. The checking and inspection scripts write summaries under `outputs/`. Raw source files and ID-bearing intermediate audits are not committed.

Eligibility requires a known registration date on or before day 63. OULAD uses exactly `-1` to mean that no unregistration date was recorded; other unregistration dates on or before day 63 are excluded. See [the dataset guide](dataset_guide.md), [the cohort and label rules](how_risk_is_defined.md), and [the quality notes](data_quality_notes.md) for the full decisions and limitations.

OULAD is distributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Cite Kuzilek, Hlosta, and Zdrahal (2017), *Scientific Data*, 4, 170171 ([DOI](https://doi.org/10.1038/sdata.2017.171)) and describe the project’s preprocessing changes.
