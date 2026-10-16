# Day-63 eligibility correction

The previous processing rule treated all recorded unregistration values at or before day 63 as withdrawals. The corrected rule recognizes exactly `-1` as OULAD's no-recorded-unregistration sentinel. This distinction restores 145 eligible records whose final outcome is Withdrawn. Other negative unregistration dates remain excluded as pre-course withdrawals.

| Measure | Previous rule | Corrected rule |
|---|---:|---:|
| Eligible student-course records | 26,277 | 26,422 |
| `at_risk = 0` | 15,381 | 15,381 |
| `at_risk = 1` | 10,896 | 11,041 |

The corrected eligibility rule also requires a known registration date on or before day 63. Nine records with missing registration dates and eight registered after day 63 are excluded. The corrected cohort is stored in `data/processed/student_risk_at_day_63.csv`.
