"""Build the EduAI OULAD day-63 cohort, features, and audit outputs."""

from pathlib import Path
import json
import os

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = Path(os.environ.get("EDUAI_RAW_DIR", ROOT / "data" / "raw"))
OUT = ROOT / "outputs"
PROCESSED = ROOT / "data" / "processed"
CUTOFF = 63
KEY = ["code_module", "code_presentation", "id_student"]
REQUIRED = {
    "studentInfo.csv": {"code_module", "code_presentation", "id_student", "gender", "region", "highest_education", "imd_band", "age_band", "num_of_prev_attempts", "studied_credits", "disability", "final_result"},
    "studentRegistration.csv": {"code_module", "code_presentation", "id_student", "date_registration", "date_unregistration"},
    "assessments.csv": {"id_assessment", "code_module", "code_presentation", "date"},
    "studentAssessment.csv": {"id_assessment", "id_student", "date_submitted"},
    "studentVle.csv": {"code_module", "code_presentation", "id_student", "id_site", "date", "sum_click"},
    "vle.csv": {"id_site", "code_module", "code_presentation", "activity_type"},
    "courses.csv": {"code_module", "code_presentation"},
}
NUMERIC = {
    "studentRegistration.csv": ["date_registration", "date_unregistration"],
    "assessments.csv": ["date"],
    "studentAssessment.csv": ["date_submitted"],
    "studentVle.csv": ["date", "sum_click"],
}


def load_sources():
    sources = {}
    for filename, required in REQUIRED.items():
        path = RAW / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required OULAD file is missing: {path}")
        frame = pd.read_csv(path, na_values=["?"], keep_default_na=True)
        missing = sorted(required - set(frame.columns))
        if missing:
            raise ValueError(f"{filename} is missing required columns: {missing}")
        for column in NUMERIC.get(filename, []):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        sources[filename] = frame
    return sources


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    s = load_sources()
    info = s["studentInfo.csv"].copy()
    reg = s["studentRegistration.csv"].copy()
    assessments = s["assessments.csv"]
    student_assessments = s["studentAssessment.csv"]
    student_vle = s["studentVle.csv"]
    vle = s["vle.csv"]

    # Fail early on key constraints so source changes cannot silently inflate rows.
    key_checks = {
        "studentInfo student-course key": (info, KEY),
        "studentRegistration student-course key": (reg, KEY),
        "assessment ID": (assessments, ["id_assessment"]),
        "studentAssessment assessment-student key": (student_assessments, ["id_assessment", "id_student"]),
        "course key": (s["courses.csv"], ["code_module", "code_presentation"]),
    }
    for label, (frame, columns) in key_checks.items():
        if frame.duplicated(columns).any():
            raise ValueError(f"Duplicate {label} found ({int(frame.duplicated(columns).sum())} rows)")
    unknown_results = sorted(set(info["final_result"].dropna()) - {"Fail", "Withdrawn", "Pass", "Distinction"})
    if unknown_results:
        raise ValueError(f"Unexpected final_result values: {unknown_results}")

    # OULAD uses exactly -1 to mean no recorded unregistration. Other recorded
    # dates on or before the cutoff, including other negative dates, are pre-course
    # withdrawals and make the record ineligible at day 63.
    base = info.merge(reg[KEY + ["date_registration", "date_unregistration"]], on=KEY,
                      how="left", validate="one_to_one", suffixes=("", "_registration"))

    # Eligible assessments require known due dates, due by day 63, and a known
    # submission date by day 63. Assessment scores are intentionally unused.
    assess = student_assessments.merge(
        assessments[["id_assessment", "code_module", "code_presentation", "date"]],
        on="id_assessment", how="inner", validate="many_to_one")
    assess = assess.loc[assess["date"].notna() & assess["date"].ge(0) & assess["date"].le(CUTOFF)
                        & assess["date_submitted"].notna() & assess["date_submitted"].le(CUTOFF)]
    assess = assess.merge(info[KEY], on=KEY, how="inner", validate="many_to_one")
    due_assessments = assessments.loc[
        assessments["date"].notna() & assessments["date"].ge(0) & assessments["date"].le(CUTOFF)
    ]
    due_features = due_assessments.groupby(KEY[:2]).agg(
        assessments_due_by_cutoff=("id_assessment", "nunique")).reset_index()
    base = base.merge(due_features, on=KEY[:2], how="left", validate="many_to_one")
    base["assessments_due_by_cutoff"] = base["assessments_due_by_cutoff"].fillna(0).astype("int64")
    assess_features = assess.groupby(KEY).agg(
        assessments_submitted_by_cutoff=("id_assessment", "nunique")).reset_index()
    base = base.merge(assess_features, on=KEY, how="left", validate="one_to_one")
    base["assessments_submitted_by_cutoff"] = base["assessments_submitted_by_cutoff"].fillna(0).astype("int64")
    base["assessments_not_submitted_by_cutoff"] = (
        base["assessments_due_by_cutoff"] - base["assessments_submitted_by_cutoff"]
    )
    if base["assessments_not_submitted_by_cutoff"].lt(0).any():
        raise ValueError("Submitted assessment count exceeds the due assessment count")

    # Keep all source VLE rows, including exact repeats, per project decision.
    activity = student_vle.loc[student_vle["date"].notna() & student_vle["date"].le(CUTOFF)].merge(
        vle[["id_site", "code_module", "code_presentation", "activity_type"]],
        on=["id_site", "code_module", "code_presentation"], how="left", validate="many_to_one")
    engagement = activity.groupby(KEY).agg(
        vle_clicks_by_cutoff=("sum_click", "sum"),
        vle_active_days_by_cutoff=("date", "nunique"),
        vle_active_sites_by_cutoff=("id_site", "nunique"),
        vle_log_rows_by_cutoff=("sum_click", "size"),
    ).reset_index()
    activity_type = activity.pivot_table(index=KEY, columns="activity_type", values="sum_click",
                                         aggfunc="sum", fill_value=0)
    activity_type.columns = ["vle_clicks_" + str(c).strip().lower().replace(" ", "_") + "_by_cutoff"
                             for c in activity_type.columns]
    activity_type = activity_type.reset_index()
    base = base.merge(engagement, on=KEY, how="left", validate="one_to_one")
    base = base.merge(activity_type, on=KEY, how="left", validate="one_to_one")
    for col in base.columns:
        if col.startswith("vle_"):
            base[col] = base[col].fillna(0).astype("int64")
    base["imd_band"] = base["imd_band"].replace("?", pd.NA)
    base.insert(0, "prediction_cutoff_day", CUTOFF)
    base.insert(1, "prediction_cutoff_rule", f"course day <= {CUTOFF}")
    base = base.sort_values(KEY).reset_index(drop=True)
    if base.duplicated(KEY).any():
        raise ValueError("Feature dataset contains duplicate student-course keys")
    base.to_csv(OUT / "oulad_at_risk_day63_prepared.csv", index=False)

    # One row per roster key with explicit and mutually exclusive exclusion reason.
    reason = pd.Series("eligible", index=base.index, dtype="object")
    reason.loc[base["date_registration"].isna()] = "missing_registration_date"
    reason.loc[base["date_registration"].notna() & base["date_registration"].gt(CUTOFF)] = "registered_after_day63"
    unregistration = base["date_unregistration"]
    withdrawn = unregistration.notna() & unregistration.ne(-1) & unregistration.le(CUTOFF)
    reason.loc[withdrawn] = "withdrew_by_day63"
    audit = base[KEY + ["date_registration", "date_unregistration", "final_result"]].copy()
    audit["eligibility_status"] = reason
    audit["exclusion_reason"] = reason.where(reason.ne("eligible"), "")
    audit.to_csv(OUT / "oulad_day63_source_audit.csv", index=False)
    audit.loc[audit["eligibility_status"].ne("eligible")].to_csv(OUT / "oulad_day63_exclusions.csv", index=False)

    eligible = base.loc[reason.eq("eligible")].copy()
    eligible["at_risk"] = eligible["final_result"].isin(["Fail", "Withdrawn"]).astype("int8")
    if eligible["final_result"].isna().any():
        raise ValueError("Eligible rows have missing final_result")
    eligible.to_csv(OUT / "oulad_at_risk_day63_source_rows.csv", index=False)

    # Keep the outcome label and day-63 fields for later modelling, but leave
    # train/test assignment and model-specific feature handling to that stage.
    processed = eligible.drop(columns=["final_result", "id_student", "date_unregistration"])
    processed_path = PROCESSED / "student_risk_at_day_63.csv"
    processed.to_csv(processed_path, index=False)
    # Recreate the previous repository rule from the same raw roster: known
    # registration by day 63, with blank or post-cutoff unregistration dates.
    previous_eligible = base.loc[
        base["date_registration"].notna()
        & base["date_registration"].le(CUTOFF)
        & (base["date_unregistration"].isna() | base["date_unregistration"].gt(CUTOFF))
    ].copy()
    previous_keys = set(map(tuple, previous_eligible[KEY].itertuples(index=False, name=None)))
    current_keys = set(map(tuple, eligible[KEY].itertuples(index=False, name=None)))
    removed_keys = previous_keys - current_keys
    added_keys = current_keys - previous_keys
    report = {
        "cutoff_day": CUTOFF,
        "source_rows": {name: int(len(frame)) for name, frame in s.items()},
        "roster_rows": int(len(base)),
        "eligible_rows": int(len(eligible)),
        "exclusion_reasons": {str(k): int(v) for k, v in audit.eligibility_status.value_counts().items()},
        "at_risk_counts": {str(k): int(v) for k, v in eligible.at_risk.value_counts().sort_index().items()},
        "processed_rows_columns": [int(processed.shape[0]), int(processed.shape[1])],
        "processed_missing_cells": int(processed.isna().sum().sum()),
        "roster_duplicate_keys": int(base.duplicated(KEY).sum()),
        "preserved_exact_student_vle_repeats": int(student_vle.duplicated().sum()),
        "unknown_assessment_due_dates_excluded_from_feature": int(assessments["date"].isna().sum()),
        "negative_assessment_due_dates_excluded_from_feature": int(assessments["date"].lt(0).sum()),
        "eligible_due_assessment_opportunities": int(eligible["assessments_due_by_cutoff"].sum()),
        "eligible_submitted_assessment_opportunities_by_cutoff": int(eligible["assessments_submitted_by_cutoff"].sum()),
        "eligible_not_submitted_assessment_opportunities_by_cutoff": int(eligible["assessments_not_submitted_by_cutoff"].sum()),
        "outputs": ["outputs/oulad_at_risk_day63_prepared.csv", "data/processed/student_risk_at_day_63.csv",
                    "oulad_at_risk_day63_source_rows.csv", "oulad_day63_source_audit.csv",
                    "oulad_day63_exclusions.csv"],
        "audit_only_fields": ["gender", "region", "highest_education", "imd_band", "age_band",
                              "disability", "code_presentation",
                              "prediction_cutoff_day", "prediction_cutoff_rule"],
    }
    report["previous_comparison"] = {
        "previous_rule_rows": int(len(previous_eligible)),
        "new_rows": int(len(eligible)),
        "previous_keys_retained": int(len(previous_keys & current_keys)),
        "previous_keys_removed_by_corrected_rule": int(len(removed_keys)),
        "keys_added": int(len(added_keys)),
        "removed_key_examples": [list(key) for key in sorted(removed_keys)[:10]],
        "added_key_examples": [list(key) for key in sorted(added_keys)[:10]],
        "previous_target_counts": {str(k): int(v) for k, v in previous_eligible.final_result.isin(["Fail", "Withdrawn"]).astype("int8").value_counts().sort_index().items()},
        "new_target_counts": report["at_risk_counts"],
    }
    (OUT / "day63_preprocessing_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    comparison = [
        "# Day-63 eligibility comparison", "",
        "The previous rule treated every recorded unregistration value at or before day 63 as a withdrawal. The corrected rule recognizes exactly -1 as OULAD's no-recorded-unregistration sentinel, while excluding other dates on or before day 63. It also requires a known registration date on or before day 63.", "",
        "| Measure | Previous rule | Corrected rule |", "|---|---:|---:|",
        f"| Eligible student-course rows | {len(previous_eligible):,} | {len(eligible):,} |",
        f"| Previous keys retained | — | {len(previous_keys & current_keys):,} |",
        f"| Previous keys removed by corrected rule | — | {len(removed_keys):,} |",
        f"| Keys added | — | {len(added_keys):,} |", "",
        "The key counts above are computed directly from the raw roster using both rules. The corrected cohort is the one used for the rebuilt dataset.", "",
    ]
    (OUT / "day63_previous_comparison.md").write_text("\n".join(comparison), encoding="utf-8")
    lines = ["EduAI Day-63 preprocessing report", "", f"Cutoff: inclusive course day {CUTOFF}",
             f"Roster rows: {len(base):,}",
             f"Eligible student-course rows: {len(eligible):,}", "", "Exclusions:"]
    lines += [f"- {k}: {v:,}" for k, v in report["exclusion_reasons"].items() if k != "eligible"]
    lines += ["", f"Target counts (0, 1): {report['at_risk_counts']}",
              f"Processed table shape: {processed.shape[0]:,} x {processed.shape[1]}",
              f"Missing cells in processed table: {int(processed.isna().sum().sum())}",
              f"Exact repeated studentVle rows retained: {int(student_vle.duplicated().sum()):,}",
              f"Unknown assessment due dates: {int(assessments['date'].isna().sum())}",
              f"Eligible due assessment opportunities by day 63: {int(eligible['assessments_due_by_cutoff'].sum()):,}",
              f"Submitted opportunities by day 63: {int(eligible['assessments_submitted_by_cutoff'].sum()):,}",
              f"Not submitted by day 63: {int(eligible['assessments_not_submitted_by_cutoff'].sum()):,}"]
    (OUT / "day63_preprocessing_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"Processed table: {processed_path}")


if __name__ == "__main__":
    main()
