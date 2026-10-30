"""Train and evaluate machine learning models for academic risk."""

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

from preparation import build_preprocessor
from Settings import OUTPUT_FOLDER, RANDOM_STATE, make_output_folder


def run_risk_models(X_train, y_train, X_test, y_test):
    """Train and evaluate Logistic Regression and Random Forest."""

    print("\nMACHINE LEARNING MODEL TRAINING")
    print("-" * 50)

    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            random_state=RANDOM_STATE
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            random_state=RANDOM_STATE
        )
    }

    results = []

    for name, model in models.items():

        print(f"\nTraining {name}...")

        pipeline = Pipeline([
            ("preprocessor", build_preprocessor(X_train)),
            ("classifier", model)
        ])

        # Train the model
        pipeline.fit(X_train, y_train)

        # Make predictions
        predictions = pipeline.predict(X_test)

        # Calculate prediction probabilities
        probabilities = pipeline.predict_proba(X_test)[:, 1]

        # Calculate evaluation metrics
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(
            y_test, predictions, zero_division=0
        )
        recall = recall_score(
            y_test, predictions, zero_division=0
        )
        f1 = f1_score(
            y_test, predictions, zero_division=0
        )
        roc_auc = roc_auc_score(y_test, probabilities)

        # Calculate confusion matrix
        matrix = confusion_matrix(
            y_test, predictions, labels=[0, 1]
        )

        print(f"\n{name} Results:")
        print(f"Accuracy:  {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-score:  {f1:.4f}")
        print(f"ROC-AUC:   {roc_auc:.4f}")

        print("\nConfusion Matrix:")
        print(matrix)

        # Store evaluation results
        results.append({
            "model": name,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "roc_auc": roc_auc
        })

    # Save model comparison results
    make_output_folder()

    results_df = pd.DataFrame(results)

    output_path = OUTPUT_FOLDER / "model_comparison.csv"

    results_df.to_csv(output_path, index=False)

    print("\nModel comparison saved successfully.")
    print(f"File: {output_path}")

    return results_df
