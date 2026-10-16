# AI Student Tracking System

## Project overview

This Business Analysis 3.2 project explores an AI-supported early-warning approach for student support. The current implementation work prepares and documents a day-63 cohort from the Open University Learning Analytics Dataset (OULAD). It is a research prototype using historical public data, not a tool validated for current students at VUT.

## Week 1: data preparation

The processed cohort contains 26,422 student-course records from seven modules and 22 presentations. Each record represents one student in one module presentation. The outcome label, `at_risk`, is 1 for a later `Fail` or `Withdrawn` result and 0 for `Pass` or `Distinction`.

The corrected eligibility rule requires a known registration date on or before course day 63. OULAD uses exactly `-1` for no recorded unregistration; those records remain eligible when the registration rule is met. Other unregistration dates on or before day 63 indicate the student had already left and are excluded. This correction restores 145 eligible records.

Assessment features count known, nonnegative due dates up to day 63, submissions recorded by that date, and due assessments without a recorded submission by then. VLE activity after day 63 is excluded. Exact repeated VLE rows are retained because their provenance is unclear. Assessment scores are not used because their availability dates are not provided.

The versioned CSV omits direct student IDs, final-result text, and unregistration dates. Demographic fields remain available for later subgroup review. The processed file has no training/test assignment.

## Rebuild the dataset

Place the seven OULAD source CSV files in `data/raw/`, then run these commands from the repository root:

```powershell
python -m pip install -r requirements-data-prep.txt
python scripts\prepare_dataset.py
python scripts\check_dataset.py
python scripts\inspect_oulad.py
```

The scripts write the processed table to `data/processed/` and quality reports to `outputs/`. Raw data and ID-bearing audit files are not committed.

## Data source and attribution

OULAD is distributed under the [Creative Commons Attribution 4.0 International licence](https://creativecommons.org/licenses/by/4.0/). Cite Kuzilek, Hlosta, and Zdrahal (2017), *Scientific Data*, 4, 170171, [doi:10.1038/sdata.2017.171](https://doi.org/10.1038/sdata.2017.171), and describe the preprocessing changes when reusing the derived data.

See [the processed-data guide](data/processed/README.md), [the cohort and label rules](data/processed/how_risk_is_defined.md), and [the quality notes](data/processed/data_quality_notes.md) for details and limitations.
