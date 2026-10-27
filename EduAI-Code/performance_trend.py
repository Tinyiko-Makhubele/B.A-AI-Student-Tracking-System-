"""Analyse academic performance and engagement changes."""

import pandas as pd
from Settings import DATA_PATH, OUTPUT_FOLDER, make_output_folder


def run_performance_trend():
    """Summarise student performance and engagement indicators."""

    data = pd.read_csv(DATA_PATH)

    print("\nSTUDENT PERFORMANCE TREND ANALYSIS")
    print("-" * 50)

    # Classify changes in academic marks
    data["performance_trend"] = "Stable"

    data.loc[data["mark_change"] > 0, "performance_trend"] = "Improving"
    data.loc[data["mark_change"] < 0, "performance_trend"] = "Declining"

    # Classify changes in student engagement
    data["engagement_trend"] = "Stable"

    data.loc[data["engagement_change"] > 0, "engagement_trend"] = "Increasing"
    data.loc[data["engagement_change"] < 0, "engagement_trend"] = "Decreasing"

    # Identify records where mark change was originally missing
    if "mark_change_was_missing" in data.columns:
        missing = data["mark_change_was_missing"] == 1
        data.loc[missing, "performance_trend"] = "Unknown"

    print("\nAcademic performance trends:")
    print(data["performance_trend"].value_counts())

    print("\nStudent engagement trends:")
    print(data["engagement_trend"].value_counts())

    print("\nAverage marks by academic risk category:")
    print(data.groupby("at_risk")["average_mark"].mean().round(2))

    print("\nAverage missed assessments by academic risk category:")
    print(data.groupby("at_risk")["missed_assessments"].mean().round(2))

    # Save the results
    make_output_folder()

    summary = data[
        [
            "record_key",
            "performance_trend",
            "engagement_trend",
            "average_mark",
            "latest_mark",
            "missed_assessments",
            "at_risk",
        ]
    ]

    summary.to_csv(
        OUTPUT_FOLDER / "student_performance_trends.csv",
        index=False
    )

    print("\nPerformance trend results saved successfully.")


if __name__ == "__main__":
    run_performance_trend()