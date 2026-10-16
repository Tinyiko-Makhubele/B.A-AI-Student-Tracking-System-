# How the day-63 cohort and outcome are defined

This note describes the cohort and outcome label used in the processed OULAD table. It does not describe a trained or validated prediction model.

## Cohort

The prediction record is one student in one module presentation. The prototype checkpoint is the end of course day 63. A record is included only if its registration date is known and no later than day 63, and the student had not unregistered by that date.

OULAD uses exactly `date_unregistration = -1` as a sentinel for no recorded unregistration. That value must not be interpreted as a pre-course withdrawal. Other recorded unregistration dates at or before day 63, including other negative dates, are excluded. A blank unregistration date is also treated as no recorded date. This corrected rule restores 145 records that the previous preparation incorrectly excluded.

The resulting cohort has 26,422 records. Nine records with missing registration dates and eight records registered after day 63 are excluded, along with 6,154 records that had unregistered by the checkpoint.

## Outcome label

The source `final_result` is used to assign `at_risk`:

| Final result | `at_risk` |
|---|---:|
| Fail | 1 |
| Withdrawn | 1 |
| Pass | 0 |
| Distinction | 0 |

The label is based on the final course outcome, which occurs after the day-63 checkpoint. It is a retrospective outcome for research; it is not a diagnosis or proof that the outcome could have been prevented. The processed CSV omits `final_result` and `date_unregistration` after applying the cohort and label rules.

## Information included in the table

Assessment counts use only assessments with known, nonnegative due dates on or before day 63. A submission counts only when its recorded submission date is also on or before the checkpoint. “Not submitted” means that no submission was recorded by day 63; it does not measure understanding or engagement through other channels. Scores are not included because OULAD does not document when they became available.

VLE features use records dated on or before day 63. All exact repeated source rows are retained because the source does not establish their provenance. Student IDs are used to join source tables and verify unique student-course records, then removed from the versioned dataset. Demographic fields remain available for later aggregate review.
