from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'outputs'
OUT.mkdir(exist_ok=True)

lines = ['# Step 4 — Initial Data Quality Inspection', '']
lines += ['## Source CSV summary', '', '| File | Rows | Columns | Missing cells (`?` treated as missing) | Exact duplicate rows |', '|---|---:|---:|---:|---:|']
for path in sorted(RAW.glob('*.csv')):
    frame = pd.read_csv(path, na_values=['?'])
    lines.append(f'| `{path.name}` | {len(frame):,} | {len(frame.columns)} | {int(frame.isna().sum().sum()):,} | {int(frame.duplicated().sum()):,} |')
lines += ['', '## Source column names and inferred data types', '']
for path in sorted(RAW.glob('*.csv')):
    frame = pd.read_csv(path, na_values=['?'], nrows=1000)
    lines += [f'### `{path.name}`', '', ', '.join(f'`{col}` ({dtype})' for col, dtype in frame.dtypes.items()), '']

model_path = OUT / 'oulad_at_risk_day63_modeling.csv'
model = pd.read_csv(model_path)
audit = pd.read_csv(OUT / 'oulad_at_risk_day63_source_rows.csv')
key = ['code_module', 'code_presentation', 'id_student']
lines += [
    '## Git-ready modelling table', '',
    f'- Shape: **{len(model):,} rows × {len(model.columns)} columns**.',
    f'- Duplicate student-course keys before identifier removal: **{int(audit.duplicated(key).sum()):,}**.',
    f'- Rows with missing cells: **{int(model.isna().any(axis=1).sum()):,}**.',
    '- `final_result` and `id_student` are omitted from this versioned table. The source outcome is used only to construct `at_risk`; the split label is retained.',
    '- Target balance:', '',
    '| `at_risk` | Count | Share |', '|---:|---:|---:|'
]
for label, count in model['at_risk'].value_counts().sort_index().items():
    lines.append(f'| {int(label)} | {count:,} | {count / len(model):.1%} |')
lines += ['', '### Evaluation assignment', '', '| Split | Rows |', '|---|---:|']
for split, count in model['evaluation_split'].value_counts().sort_index().items():
    lines.append(f'| `{split}` | {count:,} |')
lines += ['', '### Modelling-table columns and inferred types', '', '| Column | Type | Missing |', '|---|---|---:|']
for col in model.columns:
    lines.append(f'| `{col}` | `{model[col].dtype}` | {int(model[col].isna().sum()):,} |')
lines += [
    '', '## Recorded observations', '',
    '- `?` is used as a missing marker in source fields; blank `date_unregistration` is expected for students who completed the course.',
    '- The primary VLE policy preserves all source rows. Exact repeats are documented as ambiguous and a deduplicated sensitivity artifact is retained.',
    '- `final_result` is used only to construct `at_risk`; it and `id_student` are omitted from the Git-ready table. The split was assigned using student IDs before they were removed. Demographic columns are for subgroup checks only; `evaluation_split` and cutoff fields are metadata, not predictors.',
    '- See `oulad_day63_data_dictionary.md` and `oulad_step3_label_feature_rules.md` for the decision log and feature/leakage rules.',
    ''
]
report = OUT / 'step4_data_quality_report.md'
report.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote {report}')
print(f'Git-ready modelling table: {len(model):,} × {len(model.columns)}; target balance: {model.at_risk.value_counts().sort_index().to_dict()}')
