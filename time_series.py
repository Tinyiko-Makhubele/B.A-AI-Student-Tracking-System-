"""Analyse student performance, risk and engagement over time."""

import pandas as pd
import matplotlib.pyplot as plt

from Settings import DATA_PATH, OUTPUT_FOLDER, make_output_folder


def run_time_series():

    print("\nTIME SERIES ANALYSIS")
    print("-" * 50)

    # Load student data
    data = pd.read_csv(DATA_PATH)

    # Summarise data by academic presentation period
    summary = data.groupby("code_presentation").agg(
        average_mark=("average_mark", "mean"),
        risk_rate=("at_risk", "mean"),
        average_engagement=("vle_clicks", "mean"),
        student_records=("at_risk", "size")
    ).sort_index()

    # Convert risk rate into a percentage
    summary["risk_rate"] *= 100

    print("\nAcademic performance across presentation periods:")
    print(summary.round(2))

    make_output_folder()

    # Save the time series summary
    summary.to_csv(
        OUTPUT_FOLDER / "time_series_summary.csv"
    )

    # Plot average academic marks
    plt.figure(figsize=(9, 5))

    plt.plot(
        summary.index,
        summary["average_mark"],
        marker="o"
    )

    plt.title("Average Academic Marks Across Presentation Periods")
    plt.xlabel("Academic Presentation Period")
    plt.ylabel("Average Mark (%)")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "academic_marks_over_time.png"
    )

    plt.close()

    # Plot academic risk rate
    plt.figure(figsize=(9, 5))

    plt.plot(
        summary.index,
        summary["risk_rate"],
        marker="o"
    )

    plt.title("Academic Risk Rate Across Presentation Periods")
    plt.xlabel("Academic Presentation Period")
    plt.ylabel("At-Risk Records (%)")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "academic_risk_over_time.png"
    )

    plt.close()

    # Plot student engagement
    plt.figure(figsize=(9, 5))

    plt.plot(
        summary.index,
        summary["average_engagement"],
        marker="o"
    )

    plt.title("Student Engagement Across Presentation Periods")
    plt.xlabel("Academic Presentation Period")
    plt.ylabel("Average VLE Clicks")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        OUTPUT_FOLDER / "student_engagement_over_time.png"
    )

    plt.close()

    print("\nTime series analysis completed successfully!")
    print("Summary and graphs saved in the outputs folder.")


if __name__ == "__main__":
    run_time_series()