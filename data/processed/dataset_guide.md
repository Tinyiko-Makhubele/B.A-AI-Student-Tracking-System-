# OULAD dataset guide

This dataset uses OULAD course records to explore whether a student may be at risk by course day 63 (about week 9). It covers all seven modules and 22 presentations. Each row represents one student in one presentation.

## How the table was prepared

Student, registration, assessment, and VLE tables were joined using their course, student, assessment, or site identifiers. We kept students still registered on day 63 and counted assessment submissions and VLE activity recorded by that date. Assessment scores were left out because OULAD does not say when they became available.

The CSV includes course context, prior study information, assessment submission counts, and overall and activity-specific VLE click counts. Demographic fields are included for subgroup checks only. The `at_risk` label is 1 for Fail or Withdrawn and 0 for Pass or Distinction.

## Evaluation split

The table has 26,292 eligible records: 10,907 labelled at risk and 15,385 not at risk. The latest presentation, 2014J, is held out for testing. Earlier records for students who also appear in 2014J are excluded from training, leaving no student overlap between the train and test groups.

## Data notes

We kept all source VLE rows because the dataset does not explain whether exact repeated rows are errors or separate click records. Removing them changes day-63 click totals by about 3.2% and affects 23,196 eligible records; the deduplicated version is kept only for sensitivity checks.

Student ID is used for grouping and splitting, then removed from the shared CSV. The outcome is used to make the label, not as an input. The cutoff and evaluation split are metadata, not predictors. No model has been trained.

For field-by-field details and quality checks, see [data_quality_notes.md](data_quality_notes.md). The label and leakage rules are in [how_risk_is_defined.md](how_risk_is_defined.md).
