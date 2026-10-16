# Week 1 implementation status

Week 1 established the prediction question, prepared the OULAD cohort, documented the target and cutoff rules, and inspected the resulting data. This remains a historical-data prototype; it does not establish that a day-63 intervention is effective at VUT.

## Completed

- Defined one student-course record as the unit of analysis and day 63 as the prototype checkpoint.
- Prepared a 26,422-record cohort across seven modules and 22 presentations.
- Corrected eligibility to treat exactly `date_unregistration = -1` as no recorded unregistration. This restores 145 eligible records. Other unregistration dates at or before day 63 are excluded.
- Defined `at_risk` as 1 for a later Fail or Withdrawn result and 0 for Pass or Distinction.
- Counted only known assessment due dates and submissions available by day 63; excluded scores because their availability dates are not documented.
- Preserved exact repeated VLE rows because their provenance is unclear, and documented the resulting limitation.
- Removed student IDs, final-result text, and unregistration dates from the versioned processed table.
- Added reproducible preparation, validation, and inspection scripts with dataset attribution.

## Limitations to resolve before operational use

Day 63 is a prototype choice that still needs comparison with a real institution’s support timeline. The `at_risk` label is retrospective, and the repeated VLE rows have uncertain provenance. Demographic fields in the dataset require careful aggregate review and are not evidence about an individual student.
