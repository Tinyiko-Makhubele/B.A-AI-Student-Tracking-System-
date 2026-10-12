# OULAD early-warning dataset: day 63

## Duplicate provenance decision

**Primary policy: preserve every source `studentVle.csv` row and aggregate its `sum_click` value. Do not drop exact repeated rows as the primary treatment.** The UCI release and OULAD paper describe the VLE table and report its 10,655,280 rows, but neither defines a unique row key or classifies repeated rows as erroneous. The CSV alone cannot prove whether an identical row is a duplicated export or a separate click-count contribution. Preserving source rows avoids deleting observations without provenance evidence. [UCI dataset record](https://archive.ics.uci.edu/dataset/349/open%2Buniversity%2Blearnin) [OULAD data paper](https://doi.org/10.1038/sdata.2017.171)

In this supplied file, exact repeats total **787,170 rows**; 73.9% of those repeated rows have `sum_click = 1`, which is consistent with—but does not prove—the possibility that they represent separate one-click records. Removing them would reduce all-course click totals by **1,262,036 clicks (3.19%)**. Through day 63, the difference is **526,347 clicks (3.22%)** across the full roster and **506,355 clicks (3.23%)** in the eligible cohort; 23,196 of 26,292 eligible student-course rows change. The deduplicated files are retained only as a sensitivity alternative.

## Step 2 suitability decision

**Suitable for a time-filtered, course-level early-warning prototype, with duplicate provenance documented as a data limitation.** OULAD contains seven modules across 22 presentations, with linked student, assessment, registration, and VLE tables. The official description says presentations begin in February (`B`) or October (`J`) and dates are relative to course start. [Open University dataset page](https://research.stem.open.ac.uk/ouanalyse/dataset/) [OULAD data paper](https://doi.org/10.1038/sdata.2017.171)

## Decisions applied

- **Population:** all seven modules across all 22 available presentations.
- **Prediction unit:** one student-course-presentation record keyed by `code_module`, `code_presentation`, and `id_student`.
- **Checkpoint:** course day 63, about week 9. At day 63 every presentation has at least one non-exam assessment due; first non-exam deadlines range from day 19 to day 61. At day 28, only 16 of 22 presentations have an assessment due. Day 63 is the more consistent common checkpoint for assessment-submission features. Confirm it matches the intended intervention window.
- **Target:** `at_risk = 1` for `Fail` or `Withdrawn`; `at_risk = 0` for `Pass` or `Distinction`.
- **Eligibility:** records with `date_unregistration <= 63` are excluded because those students were no longer enrolled at the checkpoint. Unregistration date is used only for cohort eligibility and is not exported.
- **Demographics:** retained for subgroup checks only, not as model predictors.

## Files

- `student_risk_at_day_63.csv`: Git-ready table with eligible records, binary target, and evaluation split. `final_result` and `id_student` are omitted; demographic columns remain for subgroup checks only.
- `oulad_at_risk_day63_source_rows.csv` and `oulad_at_risk_day63_split_source_rows.csv`: local audit intermediates; these retain the source outcome and student ID and are ignored by Git.
- `oulad_student_course_day63.csv`: pre-eligibility intermediate from an earlier build; do not use as the final modelling table.
- `oulad_at_risk_day63_deduplicated_sensitivity.csv` and `oulad_student_course_day63_deduplicated_sensitivity.csv`: alternative that drops exact VLE row repeats.
- `oulad_at_risk_day63_split.csv`: earlier split table using the deduplicated sensitivity treatment; use `oulad_at_risk_day63_split_source_rows.csv` for the primary treatment.

## Joins and feature construction

- `studentInfo.csv` is the student-course base and provides `final_result`.
- `studentRegistration.csv` joins by module, presentation, and student. `date_registration` is retained as baseline context. `date_unregistration` filters out records no longer eligible at day 63 and is discarded before export.
- `assessments.csv` and `studentAssessment.csv` join on `id_assessment`, then associate to the student-course key. The submission count includes assessments due on/before day 63 and submitted on/before day 63.
- `studentVle.csv` and `vle.csv` join on site, module, and presentation. All source rows are retained; engagement features sum `sum_click` for interactions dated on/before day 63.
- Assessment scores are excluded because the dataset does not record when scores became available.

## Leakage and feature roles

- `at_risk` is the target. `final_result` is used only to construct the target and is excluded from the Git-ready modelling table.
- All columns ending `_by_cutoff` use activity or submissions dated no later than course day 63.
- `date_unregistration` is not exported. It only determines whether a student was enrolled at the prediction checkpoint.
- `id_student` is for grouping and splitting only, never a predictor; it is removed from the Git-ready modelling table after the split assignment is created.
- `gender`, `region`, `highest_education`, `imd_band`, `age_band`, and `disability` are retained for subgroup checks only.
- `evaluation_split` is evaluation metadata, not a predictor. The cutoff fields are also metadata and should not be used as model inputs.
- Exclude identifier fields from model inputs unless intentionally encoded as categorical course context.

## Cohort and outcome counts

- Eligible at day 63: 26,292 student-course rows.
- Excluded for unregistration on/before day 63: 6,301 rows.
- `at_risk = 1`: 10,907; `at_risk = 0`: 15,385.
- Source outcomes in the eligible cohort: Pass 12,361; Distinction 3,024; Fail 7,044; Withdrawn 3,863.

## Evaluation split

`2014J` is held out as the latest presentation test cohort. Earlier rows for any student ID also appearing in `2014J` are marked `excluded_overlap`, so no student is represented in both train and test.

- Train: 16,309 rows (15,451 unique student IDs; 43.2% at-risk).
- Test (`2014J`): 8,791 rows (8,484 unique student IDs; 37.9% at-risk).
- Excluded overlap: 1,192 rows (1,131 unique student IDs).
- Train/test student-ID overlap: 0. Report the lower test risk rate as a cohort difference.

Report at-risk recall/sensitivity and precision alongside specificity, confusion matrix, and calibration. Choose the alert threshold based on lecturer follow-up capacity and the cost of missed students versus unnecessary alerts. Review results by course presentation and retained demographic subgroups, considering small subgroup sizes.

## Remaining limitation

The preprocessing rule is now explicit and reproducible, but the data file does not reveal the provenance of exact repeated VLE rows. If exact click totals are central to later claims, confirm the source-row semantics with the dataset maintainers or report the sensitivity alternative alongside the primary result. No model has been trained.

## Source and attribution

The source dataset is distributed by UCI under CC BY 4.0. This repository's modelling table is adapted from OULAD by joining the source tables, filtering the cohort and features at day 63, mapping the final outcome to a binary `at_risk` label, assigning an evaluation split, and omitting `final_result` and `id_student` from the exported table. Cite Kuzilek, J., Hlosta, M., and Zdrahal, Z. (2017), *Open University Learning Analytics Dataset*, *Scientific Data*, 4, 170171, https://doi.org/10.1038/sdata.2017.171. UCI dataset record: https://archive.ics.uci.edu/dataset/349/open%2Buniversity%2Blearnin.



## Step 3 rules

Operational label, predictor eligibility, leakage exclusions, and retained data-preparation observations are recorded in [how_risk_is_defined.md](how_risk_is_defined.md).
