# EduAI Step 3 — Label and Feature Rules

This document records the operational target, prediction cutoff, eligible predictors, leakage exclusions, and data-preparation observations for the OULAD prototype. It complements `dataset_guide.md`; the source observations below are retained so later revisions do not silently change the dataset interpretation.

## 1. Prediction record and eligible population

- **Row unit:** one student × module × presentation (`code_module`, `code_presentation`, `id_student`).
- **Prediction time:** course day 63 (approximately week 9), inclusive. Only information dated on or before day 63 may contribute to a predictor.
- **Eligible at prediction time:** the student must still be registered on day 63. A record with numeric `date_unregistration <= 63` is excluded from the prediction cohort. This field is used only to decide eligibility; it is never a predictor.
- The primary eligible dataset contains 26,292 records. The exclusion prevents generating warnings for students who had already left by the checkpoint.

## 2. Operational label

For eligible student-course records, derive `at_risk` from the later `studentInfo.final_result` outcome:

| `final_result` | `at_risk` |
|---|---:|
| `Fail` | 1 |
| `Withdrawn` after day 63 | 1 |
| `Pass` | 0 |
| `Distinction` | 0 |

`final_result` is retained for audit of this mapping, but both `final_result` and `at_risk` are outcome fields and must be excluded from predictors. In the eligible day-63 cohort, `at_risk = 1` has 10,907 records and `at_risk = 0` has 15,385.

## 3. Predictor rules

### Allowed by timing, subject to model-input roles

- **Course context:** `code_module` and `code_presentation` may be encoded as categorical context. Review whether their use is appropriate for each evaluation question.
- **Student history available at enrolment:** `num_of_prev_attempts`, `studied_credits`, and numeric `date_registration`.
- **Assessment activity:** `assessments_submitted_by_cutoff`, counted only for assessments due on/before day 63 with a recorded submission date on/before day 63. This measures submission activity, not achievement.
- **VLE engagement:** `vle_clicks_by_cutoff`, `vle_active_days_by_cutoff`, `vle_active_sites_by_cutoff`, `vle_log_rows_by_cutoff`, and activity-type click aggregates, built from `studentVle` rows dated on/before day 63.
- **Demographics:** `gender`, `region`, `highest_education`, `imd_band`, `age_band`, and `disability` are retained for subgroup evaluation only and are not model inputs.
- **Identifiers and bookkeeping:** `id_student` is a grouping/split key only; `prediction_cutoff_day` and `prediction_cutoff_rule` are metadata, not predictors.

The primary click aggregates preserve all source VLE rows, including exact repeats; `sum_click` is summed as supplied. The deduplicated table is a sensitivity alternative, not the primary dataset.

### Excluded to prevent leakage or invalid timing

- `final_result` and `at_risk` as predictors.
- `date_unregistration` as a predictor; it is used only for eligibility at day 63.
- VLE activity after day 63, assessments due after day 63, or submissions after day 63.
- Assessment `score` and score-derived features: OULAD has submission dates but does not state when scores became available, so they cannot be safely asserted to have been known at prediction time.
- `id_student` as a model input because it identifies an individual and can let the model memorize outcomes.

## 4. Data preparation and quality observations

The ZIP contains the seven OULAD CSV tables plus `OULAD.names`. CSV summaries below treat `?` as a missing-value marker; blank `date_unregistration` values are expected for students who completed the course.

| Source table | Rows × columns | Missing values or repeated rows observed |
|---|---:|---|
| `assessments.csv` | 206 × 6 | 11 missing assessment dates (`?`) |
| `courses.csv` | 22 × 3 | None observed |
| `studentAssessment.csv` | 173,912 × 5 | 173 missing scores (`?`) |
| `studentInfo.csv` | 32,593 × 12 | 1,111 missing `imd_band` values (`?`) |
| `studentRegistration.csv` | 32,593 × 5 | 45 missing registration dates; 22,521 blank unregistration dates |
| `studentVle.csv` | 10,655,280 × 6 | 787,170 exact repeated rows; no missing cells |
| `vle.csv` | 6,364 × 6 | 5,243 missing `week_from` and `week_to` values each |

Additional preparation checks and decisions:

- No duplicate student-course key was found in `studentInfo` or `studentRegistration`; assessment IDs were unique; `studentAssessment` had no repeated `(id_assessment, id_student)` pair.
- Student-course rows were joined using module, presentation, and student keys; assessment rows via `id_assessment`; VLE metadata via site, module, and presentation. The resulting primary dataset has one row per eligible student-course key.
- `?` date and score markers were parsed as missing for temporal/assessment processing. Missing assessment dates cannot define an eligible cutoff assessment; missing assessment scores are not used. Missing `imd_band` values remain unknown for subgroup analysis and must not be treated as a real deprivation band.
- The exact VLE repeats cannot be classified from this CSV alone as duplicated exports or separate click contributions. Preserving all source rows avoids silently deleting them. Removing exact repeats changes through-day-63 click totals by 3.22% across the full roster and 3.23% in the eligible cohort; use the deduplicated alternative only for sensitivity comparison.
- The prediction checkpoint was selected after checking assessment deadlines: all 22 presentations have at least one non-exam assessment due by day 63; at day 28 only 16 of 22 do. Confirm day 63 remains operationally early enough for lecturer outreach.

## 5. Current artifact and split

- Git-ready modelling table: `student_risk_at_day_63.csv` (target and evaluation split retained; `final_result` and `id_student` omitted).
- Local audit intermediates: `oulad_at_risk_day63_source_rows.csv` and `oulad_at_risk_day63_split_source_rows.csv` (retain source outcome and student ID; ignored by Git).
- `2014J` is the test presentation; earlier rows for students also present in `2014J` are excluded from training. The split has zero student-ID overlap.
- The split is an evaluation design, not a trained model. Demographic fields remain available for subgroup checks only.
