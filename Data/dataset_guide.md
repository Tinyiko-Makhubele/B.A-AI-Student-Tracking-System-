# OULAD dataset guide

## Source and purpose

The Open University Learning Analytics Dataset (OULAD) contains linked records on students, course presentations, registration, assessments, and virtual learning environment (VLE) activity. This project prepares historical course records to explore information that was available by a chosen point in the course. OULAD covers seven modules across 22 presentations.

Each row in the processed table represents one student in one module presentation. The project uses the end of course day 63 as a prototype checkpoint. Whether that timing would leave enough time for staff support at another institution has not been established.

## Cohort and outcome

The processed cohort contains 26,422 records. A record is included when the registration date is known and on or before day 63, and no unregistration had been recorded by then. OULAD dates are measured from course day 0. Exactly `-1` means no unregistration was recorded; other values at or before day 63 represent a prior withdrawal and are excluded. A blank unregistration date also means that no date was recorded.

The label `at_risk` is 1 for a final result of Fail or Withdrawn and 0 for Pass or Distinction. The cohort includes 11,041 at-risk and 15,381 not-at-risk records. This is a retrospective outcome label; it does not show that a later withdrawal was knowable at day 63. The processed CSV omits `id_student`, `final_result`, and `date_unregistration`.

## Features and preparation

The table includes course and prior-study context, assessment counts, and VLE activity recorded by day 63. Assessment counts distinguish known assessments due by the checkpoint, submissions recorded by then, and due assessments with no recorded submission by then. That last count does not establish a lack of engagement or learning. Assessment scores are excluded because the source does not say when they became available.

All rows in `studentVle.csv`, including exact repeats, are retained. The source does not establish whether repeated rows are duplicated exports or separate click records, so removing them could discard valid activity. There are 787,170 exact repeated rows in the source table; deduplication is appropriate only as a sensitivity check.

The processed table contains no model-specific encoding or train/test assignment. Demographic fields are retained for later review, not as evidence of individual circumstances.

## Reuse and citation

OULAD is distributed under the [Creative Commons Attribution 4.0 International licence](https://creativecommons.org/licenses/by/4.0/). Cite Kuzilek, J., Hlosta, M., and Zdrahal, Z. (2017), “Open University Learning Analytics dataset,” *Scientific Data*, 4, 170171, [doi:10.1038/sdata.2017.171](https://doi.org/10.1038/sdata.2017.171). This repository adapts the source tables by joining them, applying the day-63 cohort and feature rules, assigning the retrospective outcome label, and removing direct student identifiers and later outcomes from the processed table.
