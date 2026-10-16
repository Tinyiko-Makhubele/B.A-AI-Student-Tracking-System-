from pathlib import Path
import os
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get('EDUAI_RAW_DIR', ROOT / 'data' / 'raw'))
OUT = ROOT / 'outputs'
PROCESSED = ROOT / 'data' / 'processed'
OUT.mkdir(exist_ok=True)

lines = ['# Day-63 data quality summary', '']
lines += ['## Summary of source tables', '', '| File | Rows | Columns | Missing cells (`?` treated as missing) | Exact duplicate rows |', '|---|---:|---:|---:|---:|']
for path in sorted(RAW.glob('*.csv')):
    frame = pd.read_csv(path, na_values=['?'])
    lines.append(f'| `{path.name}` | {len(frame):,} | {len(frame.columns)} | {int(frame.isna().sum().sum()):,} | {int(frame.duplicated().sum()):,} |')
lines += ['', '## Source columns and inferred types', '']
for path in sorted(RAW.glob('*.csv')):
    frame = pd.read_csv(path, na_values=['?'], nrows=1000)
    lines += [f'### `{path.name}`', '', ', '.join(f'`{col}` ({dtype})' for col, dtype in frame.dtypes.items()), '']

processed_path = PROCESSED / 'student_risk_at_day_63.csv'
processed = pd.read_csv(processed_path)
audit = pd.read_csv(OUT / 'oulad_at_risk_day63_source_rows.csv')
key = ['code_module', 'code_presentation', 'id_student']
lines += [
    '## Processed cohort table', '',
    f'- Shape: **{len(processed):,} rows × {len(processed.columns)} columns**.',
    f'- Duplicate student-course keys before identifier removal: **{int(audit.duplicated(key).sum()):,}**.',
    f'- Rows with one or more missing values: **{int(processed.isna().any(axis=1).sum()):,}**.',
    '- The processed table omits `final_result`, `id_student`, and `date_unregistration`. The source outcome is used to create the `at_risk` label.',
    '- Target balance:', '',
    '| `at_risk` | Count | Share |', '|---:|---:|---:|'
]
for label, count in processed['at_risk'].value_counts().sort_index().items():
    lines.append(f'| {int(label)} | {count:,} | {count / len(processed):.1%} |')
lines += ['', '### Processed-table columns and inferred types', '', '| Column | Type | Missing |', '|---|---|---:|']
for col in processed.columns:
    lines.append(f'| `{col}` | `{processed[col].dtype}` | {int(processed[col].isna().sum()):,} |')
lines += [
    '', '## Notes on interpretation', '',
    '- In the source files, `?` marks missing values. A blank `date_unregistration` means no date was recorded.',
    '- All VLE source rows are retained. The files do not show whether exact repeats are duplicate exports or separate click records, so the primary table does not remove them.',
    '- Student IDs are used to join source tables and check unique student-course records, then removed. Demographic fields are retained in the processed table; no model has been fitted at this stage.',
    '- See `../data/processed/dataset_guide.md` and `../data/processed/how_risk_is_defined.md` for the cohort, feature, and leakage decisions.',
    ''
]
report = OUT / 'step4_data_quality_report.md'
report.write_text('\n'.join(lines), encoding='utf-8')
print(f'Wrote {report}')
print(f'Processed cohort table: {len(processed):,} × {len(processed.columns)}; target balance: {processed.at_risk.value_counts().sort_index().to_dict()}')
