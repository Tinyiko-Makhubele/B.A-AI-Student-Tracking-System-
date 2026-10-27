"""Evaluate Logistic Regression and Random Forest results."""

import pandas as pd
from Settings import OUTPUT_FOLDER


def run_model_evaluation():
    """Display and compare saved model performance results."""

    results_path = OUTPUT_FOLDER / "model_comparison.csv"

    if not results_path.exists():
        print("Model comparison results not found.")
        print("Please run the risk models first.")
        return

    results = pd.read_csv(results_path)

    print("\nMODEL EVALUATION")
    print("-" * 50)

    print("\nModel performance comparison:")
    print(results.to_string(index=False))

    best_model = results.loc[results["f1"].idxmax()]

    print("\nBest model based on F1-score:")
    print(best_model["model"])

    print(f"Accuracy: {best_model['accuracy']:.2%}")
    print(f"Precision: {best_model['precision']:.2%}")
    print(f"Recall: {best_model['recall']:.2%}")
    print(f"F1-score: {best_model['f1']:.2%}")
    print(f"ROC-AUC: {best_model['roc_auc']:.2%}")

    print("\nNote: Model performance should be interpreted")
    print("alongside the risks of missing at-risk students.")


if __name__ == "__main__":
    run_model_evaluation()