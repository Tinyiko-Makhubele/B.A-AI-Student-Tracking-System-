# Step 4 — Initial data-quality inspection

The report summarizes the supplied OULAD release and the corrected, de-identified day-63 cohort. It is a data-preparation check, not an evaluation of a predictive model.

## Source-table checks

| Source table | Rows | Columns | Missing cells / repeated rows |
|---|---:|---:|---|
| `assessments.csv` | 206 | 6 | 11 missing due dates |
| `courses.csv` | 22 | 3 | None reported |
| `studentAssessment.csv` | 173,912 | 5 | 173 missing values |
| `studentInfo.csv` | 32,593 | 12 | 1,111 missing values |
| `studentRegistration.csv` | 32,593 | 5 | 22,566 blank unregistration dates |
| `studentVle.csv` | 10,655,280 | 6 | 787,170 exact repeated rows |
| `vle.csv` | 6,364 | 6 | 10,486 missing `week_from` / `week_to` cells |

The literal `?` marker is treated as missing. Source keys used for student-course joins and assessment/VLE aggregation are checked by `prepare_dataset.py` before the cohort is built.

## Corrected processed cohort

- Shape: **26,422 rows × 40 columns**.
- Unique student-course records: **26,422**.
- Missing values: **999**, all in `imd_band`.
- The table omits `id_student`, `final_result`, `date_unregistration`, and any train/test assignment.

| `at_risk` | Count | Share |
|---:|---:|---:|
| 0 | 15,381 | 58.2% |
| 1 | 11,041 | 41.8% |

The eligibility correction treats exactly `date_unregistration = -1` as no recorded unregistration. It restores 145 eligible records that were previously excluded. Other unregistration dates at or before day 63 remain excluded. Nine records with missing registration dates and eight registered after day 63 are also excluded.

## Interpretation

All VLE source rows, including exact repeats, are retained because the release does not establish whether repeated rows are duplicate exports or separate click records. Assessment scores are excluded because their availability dates are not documented. The positive label is a later outcome and should be read as a retrospective research label, not a current diagnosis.
