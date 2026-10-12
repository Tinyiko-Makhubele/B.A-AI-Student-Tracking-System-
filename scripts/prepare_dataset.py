from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)
CUTOFF = 63
KEY = ['code_module', 'code_presentation', 'id_student']

info = pd.read_csv(RAW / 'studentInfo.csv')
registration = pd.read_csv(RAW / 'studentRegistration.csv')
assessments = pd.read_csv(RAW / 'assessments.csv')
student_assessments = pd.read_csv(RAW / 'studentAssessment.csv')
student_vle = pd.read_csv(RAW / 'studentVle.csv')
vle = pd.read_csv(RAW / 'vle.csv')

for frame, col in [
    (registration, 'date_registration'),
    (registration, 'date_unregistration'),
    (assessments, 'date'),
    (student_assessments, 'date_submitted'),
    (student_vle, 'date'),
    (student_vle, 'sum_click'),
]:
    frame[col] = pd.to_numeric(frame[col], errors='coerce')

assert not info.duplicated(KEY).any()
assert not registration.duplicated(KEY).any()
assert not assessments.duplicated(['id_assessment']).any()
assert not student_assessments.duplicated(['id_assessment', 'id_student']).any()

# Baseline enrolment/student fields; unregistration is kept out of predictors.
base = info.merge(
    registration[KEY + ['date_registration']],
    on=KEY, how='left', validate='one_to_one'
)

# Count only submissions for assessments due by the checkpoint and recorded by it.
assessment_rows = student_assessments.merge(
    assessments[['id_assessment', 'code_module', 'code_presentation', 'date']],
    on='id_assessment', how='inner', validate='many_to_one'
)
assessment_rows = assessment_rows.loc[
    assessment_rows['date'].le(CUTOFF)
    & assessment_rows['date_submitted'].le(CUTOFF)
].merge(info[KEY], on=KEY, how='inner', validate='many_to_one')
assessment_features = assessment_rows.groupby(KEY).agg(
    assessments_submitted_by_cutoff=('id_assessment', 'nunique'),
).reset_index()
base = base.merge(assessment_features, on=KEY, how='left', validate='one_to_one')
base['assessments_submitted_by_cutoff'] = base['assessments_submitted_by_cutoff'].fillna(0).astype('int64')

# Preserve every source VLE row; the data documentation does not establish
# that exact repeats are invalid. Aggregate only events dated by the checkpoint.
activity_rows = student_vle.loc[student_vle['date'].le(CUTOFF)].merge(
    vle[['id_site', 'code_module', 'code_presentation', 'activity_type']],
    on=['id_site', 'code_module', 'code_presentation'],
    how='left', validate='many_to_one'
)
engagement = activity_rows.groupby(KEY).agg(
    vle_clicks_by_cutoff=('sum_click', 'sum'),
    vle_active_days_by_cutoff=('date', 'nunique'),
    vle_active_sites_by_cutoff=('id_site', 'nunique'),
    vle_log_rows_by_cutoff=('sum_click', 'size'),
).reset_index()
activity_type = activity_rows.pivot_table(
    index=KEY, columns='activity_type', values='sum_click', aggfunc='sum', fill_value=0
)
activity_type.columns = [
    'vle_clicks_' + str(name).strip().lower().replace(' ', '_') + '_by_cutoff'
    for name in activity_type.columns
]
activity_type = activity_type.reset_index()
base = base.merge(engagement, on=KEY, how='left', validate='one_to_one')
base = base.merge(activity_type, on=KEY, how='left', validate='one_to_one')
for col in base.columns:
    if col.startswith('vle_'):
        base[col] = base[col].fillna(0).astype('int64')

base.insert(0, 'prediction_cutoff_day', CUTOFF)
base.insert(1, 'prediction_cutoff_rule', f'course day <= {CUTOFF}')
base = base.sort_values(KEY).reset_index(drop=True)
assert not base.duplicated(KEY).any()

# Exclude students already unregistered by the prediction checkpoint. The
# unregistration date is used only for eligibility and is not exported.
registration_end = registration[KEY + ['date_unregistration']]
eligibility = base.merge(registration_end, on=KEY, how='left', validate='one_to_one')
eligible = eligibility.loc[
    eligibility['date_unregistration'].isna()
    | eligibility['date_unregistration'].gt(CUTOFF)
].drop(columns='date_unregistration').copy()
eligible['at_risk'] = eligible['final_result'].isin(['Fail', 'Withdrawn']).astype('int8')
eligible.to_csv(OUT / 'oulad_at_risk_day63_source_rows.csv', index=False)

# Hold out the latest presentation and remove earlier rows for those same
# students from training to avoid student overlap between train and test.
test_mask = eligible['code_presentation'].eq('2014J')
test_ids = set(eligible.loc[test_mask, 'id_student'])
overlap_mask = (~test_mask) & eligible['id_student'].isin(test_ids)
eligible['evaluation_split'] = 'train'
eligible.loc[test_mask, 'evaluation_split'] = 'test'
eligible.loc[overlap_mask, 'evaluation_split'] = 'excluded_overlap'
assert not (
    set(eligible.loc[eligible['evaluation_split'].eq('train'), 'id_student'])
    & set(eligible.loc[eligible['evaluation_split'].eq('test'), 'id_student'])
)
eligible.to_csv(OUT / 'oulad_at_risk_day63_split_source_rows.csv', index=False)

# Publish a model-ready derivative: the source outcome and student identifier
# are not predictors and are omitted. The split label preserves the
# student-disjoint evaluation assignment; subgroup fields remain for audits.
modeling = eligible.drop(columns=['final_result', 'id_student'])
modeling.to_csv(OUT / 'student_risk_at_day_63.csv', index=False)

print(f'Source tables loaded from: {RAW}')
print(f'Feature rows: {len(base):,}; eligible rows: {len(eligible):,}')
print('At-risk labels:', eligible['at_risk'].value_counts().sort_index().to_dict())
print('Split rows:', eligible['evaluation_split'].value_counts().to_dict())
print('Git-ready modelling table:', modeling.shape)
print('Exact VLE rows retained:', int(student_vle.duplicated().sum()))
