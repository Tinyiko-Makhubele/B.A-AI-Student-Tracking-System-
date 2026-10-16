# Day-63 data quality notes

## Processed cohort

The corrected processed table has **26,422 rows and 40 columns**. It contains one row per eligible student-course record and no duplicate student-course keys. Target counts are:

| `at_risk` | Records | Share |
|---:|---:|---:|
| 0 | 15,381 | 58.2% |
| 1 | 11,041 | 41.8% |

There are 999 missing values, all in `imd_band`. No direct student identifier, final-result text, unregistration date, or train/test assignment is included in the processed table.

## Preparation checks and limitations

- The source OULAD tables contain 32,593 student-course roster rows. The corrected rule keeps students with a known registration date by day 63 and treats exactly `-1` as no recorded unregistration. It excludes 6,154 records withdrawn by the checkpoint, nine with unknown registration dates, and eight registered after day 63.
- The correction restores 145 eligible records with `date_unregistration = -1` and final result `Withdrawn`. Other negative unregistration dates are genuine pre-course withdrawals and remain excluded.
- Eleven assessment due dates are unknown. Only known, nonnegative due dates through day 63 contribute to the due count; only submissions recorded by the same cutoff contribute to the submitted count. Assessment scores are not used because their availability dates are unknown.
- `studentVle.csv` has 787,170 exact repeated rows. They are retained because the source does not explain whether they are duplicated exports or separate click records. Any deduplicated version should be treated as a sensitivity analysis.
- The processed table is descriptive preparation for later analysis. It has not been split for training and testing, and no model performance is reported here.

The reproducible quality report is in [`outputs/step4_data_quality_report.md`](../../outputs/step4_data_quality_report.md). The cohort and feature rules are described in [`how_risk_is_defined.md`](how_risk_is_defined.md).
