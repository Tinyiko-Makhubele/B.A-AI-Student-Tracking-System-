"""Validate the processed day-63 cohort and write a compact quality summary."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "student_risk_at_day_63.csv"
WORK = ROOT / "work"
EXPECTED_ROWS = 26_422
EXPECTED_COLUMNS = 40


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    if not DATA.is_file():
        raise FileNotFoundError(f"Run scripts/prepare_dataset.py first; missing {DATA}")
    data = pd.read_csv(DATA)
    required = {"code_module", "code_presentation", "at_risk", "date_registration"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Processed dataset is missing columns: {sorted(missing)}")
    if len(data) != EXPECTED_ROWS or len(data.columns) != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected dataset shape: {len(data)} rows x {len(data.columns)} columns")
    if data[["code_module", "code_presentation"]].isna().any().any():
        raise ValueError("Course identity fields contain missing values")
    if data["at_risk"].isna().any() or set(data["at_risk"].unique()) != {0, 1}:
        raise ValueError("at_risk must contain both binary classes and no missing values")
    forbidden = {"id_student", "final_result", "date_unregistration", "evaluation_split"}
    present_forbidden = forbidden & set(data.columns)
    if present_forbidden:
        raise ValueError(f"Processed table includes fields that should be omitted: {sorted(present_forbidden)}")
    summary = {
        "rows": len(data), "columns": len(data.columns),
        "target_counts": {str(k): int(v) for k, v in data["at_risk"].value_counts().sort_index().items()},
        "missing_cells": int(data.isna().sum().sum()),
    }
    (WORK / "day63_dataset_check.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Validated {len(data):,} rows x {len(data.columns)} columns; target={summary['target_counts']}; missing cells={summary['missing_cells']}.")


if __name__ == "__main__":
    main()
