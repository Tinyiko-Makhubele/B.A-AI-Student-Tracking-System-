"""Deep Learning model for student academic risk classification."""

import numpy as np
import pandas as pd

from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

from preparation import load_and_prepare, build_preprocessor
from Settings import OUTPUT_FOLDER, make_output_folder


def run_deep_learning():

    print("\nDEEP LEARNING - STUDENT RISK PREDICTION")
    print("-" * 55)

    # Load training and testing data
    X_train, y_train, X_test, y_test = load_and_prepare()

    # Split training data into training and validation sets
    X_train_final, X_val, y_train_final, y_val = train_test_split(
        X_train,
        y_train,
        test_size=0.2,
        random_state=42,
        stratify=y_train
    )

    print("\nDATA SPLIT")
    print("-" * 55)
    print(f"Training records: {len(X_train_final):,}")
    print(f"Validation records: {len(X_val):,}")
    print(f"Testing records: {len(X_test):,}")

    # Create neural network
    neural_network = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        max_iter=200,
        early_stopping=True,
        random_state=42
    )

    # Build preprocessing and neural network pipeline
    model = Pipeline([
        ("preprocessor", build_preprocessor(X_train_final)),
        ("classifier", neural_network)
    ])

    print("\nTraining neural network...")

    model.fit(X_train_final, y_train_final)

    print("Neural network trained successfully!")

    # Predict probabilities on validation data
    validation_probabilities = model.predict_proba(X_val)[:, 1]

    # Test different classification thresholds
    thresholds = np.round(
        np.arange(0.25, 0.76, 0.05),
        2
    )

    threshold_results = []

    print("\nVALIDATION THRESHOLD COMPARISON")
    print("-" * 55)

    for threshold in thresholds:

        validation_predictions = (
            validation_probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_val,
            validation_predictions,
            zero_division=0
        )

        recall = recall_score(
            y_val,
            validation_predictions,
            zero_division=0
        )

        f1 = f1_score(
            y_val,
            validation_predictions,
            zero_division=0
        )

        threshold_results.append({
            "threshold": float(threshold),
            "precision": precision,
            "recall": recall,
            "f1": f1
        })

    threshold_df = pd.DataFrame(threshold_results)

    print(threshold_df.round(4).to_string(index=False))

    # Select threshold with highest validation F1-score
    best_row = threshold_df.loc[
        threshold_df["f1"].idxmax()
    ]

    best_threshold = float(best_row["threshold"])

    print("\nBEST VALIDATION THRESHOLD")
    print("-" * 55)
    print(f"Selected threshold: {best_threshold:.2f}")
    print(f"Validation precision: {best_row['precision']:.4f}")
    print(f"Validation recall: {best_row['recall']:.4f}")
    print(f"Validation F1-score: {best_row['f1']:.4f}")

    # Evaluate selected model on test data
    test_probabilities = model.predict_proba(X_test)[:, 1]

    test_predictions = (
        test_probabilities >= best_threshold
    ).astype(int)

    # Calculate final evaluation metrics
    results = {
        "model": "Neural Network (Threshold Tuned)",
        "accuracy": accuracy_score(
            y_test,
            test_predictions
        ),
        "precision": precision_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        "recall": recall_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        "f1": f1_score(
            y_test,
            test_predictions,
            zero_division=0
        ),
        "roc_auc": roc_auc_score(
            y_test,
            test_probabilities
        ),
        "threshold": best_threshold
    }

    print("\nFINAL NEURAL NETWORK TEST RESULTS")
    print("-" * 55)

    print(f"Accuracy:  {results['accuracy']:.4f}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall:    {results['recall']:.4f}")
    print(f"F1-score:  {results['f1']:.4f}")
    print(f"ROC-AUC:   {results['roc_auc']:.4f}")
    print(f"Threshold: {results['threshold']:.2f}")

    print("\nConfusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            test_predictions,
            labels=[0, 1]
        )
    )

    # Save results
    make_output_folder()

    results_df = pd.DataFrame([results])

    results_df.to_csv(
        OUTPUT_FOLDER / "deep_learning_results.csv",
        index=False
    )

    threshold_df.to_csv(
        OUTPUT_FOLDER / "threshold_comparison.csv",
        index=False
    )

    print("\nDeep learning results saved successfully!")
    print("Files created:")
    print("- deep_learning_results.csv")
    print("- threshold_comparison.csv")

    return results


if __name__ == "__main__":
    run_deep_learning()