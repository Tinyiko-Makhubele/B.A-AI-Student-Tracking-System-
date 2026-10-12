# EduAI Week 1 checklist status

This status maps the Week 1 checklist to the decisions and artifacts prepared so far. The OULAD work is a research prototype using public course data; it is not evidence about current students at the project institution.

## 1. Define the prediction problem — complete

- Intended user: lecturer or academic support staff.
- Decision supported: identify currently enrolled student-course records that may need human review and outreach.
- Prediction unit: one student-course record.
- Population: all 22 OULAD course presentations.
- Prediction point: course day 63, with students already unregistered by that date excluded.
- Outcome: final result of `Fail` or `Withdrawn` is labelled at risk; `Pass` or `Distinction` is not at risk.

## 2. Select and qualify a dataset — substantially complete; two checks remain

- Selected dataset: Open University Learning Analytics Dataset (OULAD), a linked-table public dataset with assessment, registration, final-result, and dated VLE activity information.
- The joined tables support a one-row-per-student-course modelling table and pre-cutoff activity aggregation.
- Main limitations are recorded in `dataset_guide.md` and `data_quality_notes.md`, including repeated VLE rows with uncertain provenance and assessment scores without a known availability date.
- **Still to confirm:** record the applicable dataset reuse/license terms from the official distribution, and confirm with the project team that day 63 (about week 9) is early enough for the intended support workflow.

## 3. Define label and feature rules — complete

- The binary target and day-63 feature cutoff are operationally defined.
- Post-cutoff activity and submissions are excluded. Final result is used only to form the label; assessment scores are excluded because their availability time is unknown.
- Demographic fields are retained for subgroup checks, not as model inputs. Student ID is retained only for grouping/splitting.
- Rules and preparation observations are in `how_risk_is_defined.md` and `dataset_guide.md`.

## 4. Set up and inspect — complete locally; GitHub integration remains

- A local Git repository and Python environment are set up. The build and inspection scripts run against the supplied OULAD source files.
- The quality report records source and modelling-table shape, columns/types, missingness, duplicates, joins, and target balance.
- The Git-ready modelling dataset is `outputs/student_risk_at_day_63.csv`; it contains the eligible cohort, binary target, and split assignment. The raw source outcome and student ID are omitted from this versioned table.
- The work has not been added to the existing public GitHub repository yet.

## 5. Document the approach — substantially complete

- The task supports binary supervised classification, and the data dictionary notes class balance, student-disjoint evaluation, recall/sensitivity, precision, specificity, confusion matrix, calibration, and threshold selection against follow-up capacity and the costs of missed versus unnecessary alerts.
- The project README describes lecturer review and makes clear that the system supports rather than replaces lecturer judgment.
- **Still to do:** bring this project-specific framing into the repository's implementation documentation so the OULAD prototype, evaluation plan, and lecturer-in-the-loop use are presented together.

## Week 1 exit status

The prediction definition, label/feature rules, local environment, and initial quality inspection are in place. Before calling the checklist fully closed, confirm the OULAD reuse terms and the operational suitability of a day-63 alert, then integrate the implementation notes into the existing project repository. No model training is part of Week 1, and no model has been trained.
