# Step 4 — Initial Data Quality Inspection

## Source CSV summary

| File | Rows | Columns | Missing cells (`?` treated as missing) | Exact duplicate rows |
|---|---:|---:|---:|---:|
| `assessments.csv` | 206 | 6 | 11 | 0 |
| `courses.csv` | 22 | 3 | 0 | 0 |
| `studentAssessment.csv` | 173,912 | 5 | 173 | 0 |
| `studentInfo.csv` | 32,593 | 12 | 1,111 | 0 |
| `studentRegistration.csv` | 32,593 | 5 | 22,566 | 0 |
| `studentVle.csv` | 10,655,280 | 6 | 0 | 787,170 |
| `vle.csv` | 6,364 | 6 | 10,486 | 0 |

## Source column names and inferred data types

### `assessments.csv`

`code_module` (str), `code_presentation` (str), `id_assessment` (int64), `assessment_type` (str), `date` (float64), `weight` (float64)

### `courses.csv`

`code_module` (str), `code_presentation` (str), `module_presentation_length` (int64)

### `studentAssessment.csv`

`id_assessment` (int64), `id_student` (int64), `date_submitted` (int64), `is_banked` (int64), `score` (float64)

### `studentInfo.csv`

`code_module` (str), `code_presentation` (str), `id_student` (int64), `gender` (str), `region` (str), `highest_education` (str), `imd_band` (str), `age_band` (str), `num_of_prev_attempts` (int64), `studied_credits` (int64), `disability` (str), `final_result` (str)

### `studentRegistration.csv`

`code_module` (str), `code_presentation` (str), `id_student` (int64), `date_registration` (int64), `date_unregistration` (float64)

### `studentVle.csv`

`code_module` (str), `code_presentation` (str), `id_student` (int64), `id_site` (int64), `date` (int64), `sum_click` (int64)

### `vle.csv`

`id_site` (int64), `code_module` (str), `code_presentation` (str), `activity_type` (str), `week_from` (float64), `week_to` (float64)

## Git-ready modelling table

- Shape: **26,292 rows × 39 columns**.
- Duplicate student-course keys before identifier removal: **0**.
- Rows with missing cells: **7**.
- `final_result` and `id_student` are omitted from this versioned table. The source outcome is used only to construct `at_risk`; the split label is retained.
- Target balance:

| `at_risk` | Count | Share |
|---:|---:|---:|
| 0 | 15,385 | 58.5% |
| 1 | 10,907 | 41.5% |

### Evaluation assignment

| Split | Rows |
|---|---:|
| `excluded_overlap` | 1,192 |
| `test` | 8,791 |
| `train` | 16,309 |

### Modelling-table columns and inferred types

| Column | Type | Missing |
|---|---|---:|
| `prediction_cutoff_day` | `int64` | 0 |
| `prediction_cutoff_rule` | `str` | 0 |
| `code_module` | `str` | 0 |
| `code_presentation` | `str` | 0 |
| `gender` | `str` | 0 |
| `region` | `str` | 0 |
| `highest_education` | `str` | 0 |
| `imd_band` | `str` | 0 |
| `age_band` | `str` | 0 |
| `num_of_prev_attempts` | `int64` | 0 |
| `studied_credits` | `int64` | 0 |
| `disability` | `str` | 0 |
| `date_registration` | `float64` | 7 |
| `assessments_submitted_by_cutoff` | `int64` | 0 |
| `vle_clicks_by_cutoff` | `int64` | 0 |
| `vle_active_days_by_cutoff` | `int64` | 0 |
| `vle_active_sites_by_cutoff` | `int64` | 0 |
| `vle_log_rows_by_cutoff` | `int64` | 0 |
| `vle_clicks_dataplus_by_cutoff` | `int64` | 0 |
| `vle_clicks_dualpane_by_cutoff` | `int64` | 0 |
| `vle_clicks_externalquiz_by_cutoff` | `int64` | 0 |
| `vle_clicks_forumng_by_cutoff` | `int64` | 0 |
| `vle_clicks_glossary_by_cutoff` | `int64` | 0 |
| `vle_clicks_homepage_by_cutoff` | `int64` | 0 |
| `vle_clicks_htmlactivity_by_cutoff` | `int64` | 0 |
| `vle_clicks_oucollaborate_by_cutoff` | `int64` | 0 |
| `vle_clicks_oucontent_by_cutoff` | `int64` | 0 |
| `vle_clicks_ouelluminate_by_cutoff` | `int64` | 0 |
| `vle_clicks_ouwiki_by_cutoff` | `int64` | 0 |
| `vle_clicks_page_by_cutoff` | `int64` | 0 |
| `vle_clicks_questionnaire_by_cutoff` | `int64` | 0 |
| `vle_clicks_quiz_by_cutoff` | `int64` | 0 |
| `vle_clicks_repeatactivity_by_cutoff` | `int64` | 0 |
| `vle_clicks_resource_by_cutoff` | `int64` | 0 |
| `vle_clicks_sharedsubpage_by_cutoff` | `int64` | 0 |
| `vle_clicks_subpage_by_cutoff` | `int64` | 0 |
| `vle_clicks_url_by_cutoff` | `int64` | 0 |
| `at_risk` | `int64` | 0 |
| `evaluation_split` | `str` | 0 |

## Recorded observations

- `?` is used as a missing marker in source fields; blank `date_unregistration` is expected for students who completed the course.
- The primary VLE policy preserves all source rows. Exact repeats are documented as ambiguous and a deduplicated sensitivity artifact is retained.
- `final_result` is used only to construct `at_risk`; it and `id_student` are omitted from the Git-ready table. The split was assigned using student IDs before they were removed. Demographic columns are for subgroup checks only; `evaluation_split` and cutoff fields are metadata, not predictors.
- See `dataset_guide.md` and `how_risk_is_defined.md` for the decision log and feature/leakage rules.
