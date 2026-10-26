"""Student Success and Retention System prototype."""

from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score
)
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import (
    RandomizedSearchCV, StratifiedKFold, cross_validate, train_test_split
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore", category=UserWarning)

RANDOM_STATE = 42
DATA_PATH = "student_risk_at_day_63.csv"
OUTPUT_FOLDER = Path("outputs_figures")
TARGET_COLUMN = "at_risk"


def add_features(student_data):
    """Create engagement features when the required source columns are available."""
    student_data = student_data.copy()

    if {"vle_clicks_by_cutoff", "vle_active_days_by_cutoff"}.issubset(student_data.columns):
        active_days = student_data["vle_active_days_by_cutoff"].replace(0, np.nan)
        student_data["clicks_per_active_day"] = student_data["vle_clicks_by_cutoff"] / active_days

    if {"vle_clicks_forumng_by_cutoff", "vle_clicks_by_cutoff"}.issubset(student_data.columns):
        total_clicks = student_data["vle_clicks_by_cutoff"].replace(0, np.nan)
        student_data["forum_share"] = student_data["vle_clicks_forumng_by_cutoff"] / total_clicks

    if {"vle_clicks_quiz_by_cutoff", "vle_clicks_by_cutoff"}.issubset(student_data.columns):
        total_clicks = student_data["vle_clicks_by_cutoff"].replace(0, np.nan)
        student_data["quiz_share"] = student_data["vle_clicks_quiz_by_cutoff"] / total_clicks

    if "assessments_submitted_by_cutoff" in student_data.columns:
        student_data["no_assessment_yet"] = (
            student_data["assessments_submitted_by_cutoff"].fillna(0) == 0
        ).astype(int)

    return student_data


def load_and_prepare(path=DATA_PATH):
    """Load data and use its supplied train/test split when available."""
    data = pd.read_csv(path)

    if TARGET_COLUMN not in data.columns:
        raise ValueError(f"Dataset must contain a '{TARGET_COLUMN}' column.")

    data = data.drop_duplicates().copy()
    constant_columns = [
        column for column in data.columns
        if data[column].nunique(dropna=False) <= 1
    ]
    data = data.drop(columns=constant_columns, errors="ignore")

    if "evaluation_split" in data.columns:
        data = data[data["evaluation_split"] != "excluded_overlap"].copy()
        training_data = data[data["evaluation_split"] == "train"].copy()
        test_data = data[data["evaluation_split"] == "test"].copy()

        if not training_data.empty and not test_data.empty:
            training_data = training_data.drop(columns=["evaluation_split"])
            test_data = test_data.drop(columns=["evaluation_split"])
            y_train = training_data[TARGET_COLUMN].astype(int)
            y_test = test_data[TARGET_COLUMN].astype(int)
            X_train = add_features(training_data.drop(columns=[TARGET_COLUMN]))
            X_test = add_features(test_data.drop(columns=[TARGET_COLUMN]))
            return X_train, y_train, X_test, y_test

    X = data.drop(columns=[TARGET_COLUMN, "evaluation_split"], errors="ignore")
    y = data[TARGET_COLUMN].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    return add_features(X_train), y_train, add_features(X_test), y_test


def make_output_folder():
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def eda_plots(X_train, y_train):
    """Save basic exploratory data analysis plots."""
    make_output_folder()
    plot_data = X_train.copy()
    plot_data[TARGET_COLUMN] = y_train.to_numpy()

    plot_data[TARGET_COLUMN].value_counts().sort_index().plot(kind="bar", figsize=(6, 4))
    plt.title("Training data: at-risk class distribution")
    plt.xlabel("At-risk label")
    plt.ylabel("Number of students")
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER / "class_distribution.png", dpi=150)
    plt.close()

    numerical_columns = plot_data.select_dtypes(include=np.number).columns.tolist()
    numerical_columns = [column for column in numerical_columns if column != TARGET_COLUMN]
    if numerical_columns:
        plot_data[numerical_columns[:8]].hist(figsize=(12, 8), bins=20)
        plt.suptitle("Distributions of selected numeric features")
        plt.tight_layout()
        plt.savefig(OUTPUT_FOLDER / "numeric_feature_distributions.png", dpi=150)
        plt.close()

    print("\nTraining class proportions:")
    print(y_train.value_counts(normalize=True).sort_index())


def build_preprocessor(X, dense_output=False):
    """Build imputation, scaling, and categorical encoding steps."""
    categorical_columns = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numerical_columns = X.select_dtypes(include=np.number).columns.tolist()

    numerical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(
            handle_unknown="ignore",
            sparse_output=not dense_output
        )),
    ])

    return ColumnTransformer(
        [
            ("numeric", numerical_pipeline, numerical_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        sparse_threshold=0 if dense_output else 1.0,
    )


def train_ml_models(X_train, y_train):
    """Compare baseline models with stratified five-fold cross-validation."""
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, class_weight="balanced",
            random_state=RANDOM_STATE, n_jobs=-1
        ),
        "HistGradient Boosting": HistGradientBoostingClassifier(
            max_iter=150, random_state=RANDOM_STATE
        ),
    }
    cross_validation = StratifiedKFold(
        n_splits=5, shuffle=True, random_state=RANDOM_STATE
    )
    scoring = {
        "accuracy": "accuracy", "precision": "precision", "recall": "recall",
        "f1": "f1", "roc_auc": "roc_auc"
    }
    model_results = []
    trained_models = {}

    for model_name, classifier in models.items():
        dense_output = model_name == "HistGradient Boosting"
        pipeline = Pipeline([
            ("preprocessor", build_preprocessor(X_train, dense_output=dense_output)),
            ("classifier", classifier),
        ])
        scores = cross_validate(
            pipeline, X_train, y_train, cv=cross_validation,
            scoring=scoring, n_jobs=-1, error_score="raise"
        )
        model_results.append({
            "model": model_name,
            "accuracy": scores["test_accuracy"].mean(),
            "precision": scores["test_precision"].mean(),
            "recall": scores["test_recall"].mean(),
            "f1": scores["test_f1"].mean(),
            "roc_auc": scores["test_roc_auc"].mean(),
        })
        pipeline.fit(X_train, y_train)
        trained_models[model_name] = pipeline

    cv_table = pd.DataFrame(model_results).sort_values("f1", ascending=False)
    print("\nCross-validation results:")
    print(cv_table.to_string(index=False))
    make_output_folder()
    cv_table.to_csv(OUTPUT_FOLDER / "cross_validation_results.csv", index=False)
    return trained_models, cv_table


def evaluate(model, X, y, threshold=0.5, name="model"):
    """Evaluate a model and save its confusion matrix."""
    risk_probabilities = model.predict_proba(X)[:, 1]
    risk_predictions = (risk_probabilities >= threshold).astype(int)
    metrics = {
        "model": name,
        "threshold": threshold,
        "accuracy": accuracy_score(y, risk_predictions),
        "precision": precision_score(y, risk_predictions, zero_division=0),
        "recall": recall_score(y, risk_predictions, zero_division=0),
        "f1": f1_score(y, risk_predictions, zero_division=0),
    }
    if len(np.unique(y)) == 2:
        metrics["roc_auc"] = roc_auc_score(y, risk_probabilities)

    print(f"\n{name} evaluation:")
    print(pd.Series(metrics).to_string())
    print(classification_report(y, risk_predictions, zero_division=0))

    confusion = confusion_matrix(y, risk_predictions)
    make_output_folder()
    plt.figure(figsize=(5, 4))
    plt.imshow(confusion)
    plt.title(f"Confusion matrix: {name}")
    plt.xlabel("Predicted label")
    plt.ylabel("Actual label")
    plt.xticks([0, 1], ["Not at risk", "At risk"])
    plt.yticks([0, 1], ["Not at risk", "At risk"])
    for row in range(confusion.shape[0]):
        for column in range(confusion.shape[1]):
            plt.text(column, row, str(confusion[row, column]), ha="center", va="center")
    plt.tight_layout()
    plt.savefig(
        OUTPUT_FOLDER / f"confusion_matrix_{name.lower().replace(' ', '_')}.png",
        dpi=150
    )
    plt.close()
    return metrics


def fairness_check(model, X_test, y_test, group_columns):
    """Compare model precision and recall across available demographic groups."""
    risk_probabilities = model.predict_proba(X_test)[:, 1]
    risk_predictions = (risk_probabilities >= 0.5).astype(int)
    group_results = []

    for column in group_columns:
        if column not in X_test.columns:
            continue
        group_values = X_test[column].fillna("Missing")
        for group_value in group_values.unique():
            group_mask = (group_values == group_value).to_numpy()
            if not group_mask.any():
                continue
            actual_labels = y_test.iloc[np.flatnonzero(group_mask)]
            predicted_labels = risk_predictions[group_mask]
            group_results.append({
                "group_column": column,
                "group_value": str(group_value),
                "count": int(group_mask.sum()),
                "precision": precision_score(actual_labels, predicted_labels, zero_division=0),
                "recall": recall_score(actual_labels, predicted_labels, zero_division=0),
            })

    results = pd.DataFrame(group_results)
    if not results.empty:
        print("\nGroup-level performance check:")
        print(results.to_string(index=False))
        make_output_folder()
        results.to_csv(OUTPUT_FOLDER / "fairness_group_metrics.csv", index=False)
    else:
        print("\nNo requested demographic group columns were available.")
    return results


def explain(model, top_n=15):
    """Display and save feature importance where the model supports it."""
    classifier = model.named_steps["classifier"]
    preprocessor = model.named_steps["preprocessor"]

    if hasattr(classifier, "feature_importances_"):
        importance_values = classifier.feature_importances_
    elif hasattr(classifier, "coef_"):
        importance_values = np.abs(classifier.coef_[0])
    else:
        print("\nThis model does not provide built-in feature importance.")
        return pd.DataFrame()

    try:
        feature_names = preprocessor.get_feature_names_out()
    except (AttributeError, ValueError):
        feature_names = [f"feature_{index + 1}" for index in range(len(importance_values))]

    if len(feature_names) != len(importance_values):
        feature_names = [f"feature_{index + 1}" for index in range(len(importance_values))]

    feature_importance = pd.DataFrame({
        "feature": feature_names, "importance": importance_values
    }).sort_values("importance", ascending=False)

    print(f"\nTop {top_n} features:")
    print(feature_importance.head(top_n).to_string(index=False))
    make_output_folder()
    feature_importance.head(top_n).to_csv(OUTPUT_FOLDER / "feature_importance.csv", index=False)
    return feature_importance


def tune_best_model(X_train, y_train):
    """Tune a Random Forest using randomized search and cross-validation."""
    pipeline = Pipeline([
        ("preprocessor", build_preprocessor(X_train)),
        ("classifier", RandomForestClassifier(
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1
        )),
    ])
    parameter_grid = {
        "classifier__n_estimators": [150, 250, 350, 500],
        "classifier__max_depth": [None, 8, 12, 18, 25],
        "classifier__min_samples_split": [2, 5, 10],
        "classifier__min_samples_leaf": [1, 2, 4],
        "classifier__max_features": ["sqrt", "log2", 0.7],
    }
    search = RandomizedSearchCV(
        pipeline, param_distributions=parameter_grid, n_iter=15,
        scoring="f1",
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        random_state=RANDOM_STATE, n_jobs=-1, verbose=1
    )
    search.fit(X_train, y_train)
    print("\nBest tuned parameters:")
    print(search.best_params_)
    print(f"Best cross-validation F1: {search.best_score_:.3f}")
    return search.best_estimator_, search.best_params_


def choose_threshold(model, X_validation, y_validation, minimum_precision=0.60):
    """Choose a decision threshold using validation data only."""
    from sklearn.metrics import precision_recall_curve

    risk_probabilities = model.predict_proba(X_validation)[:, 1]
    precision_values, recall_values, thresholds = precision_recall_curve(
        y_validation, risk_probabilities
    )
    candidates = [
        (recall_values[index], precision_values[index], threshold)
        for index, threshold in enumerate(thresholds)
        if precision_values[index] >= minimum_precision
    ]
    if not candidates:
        print("\nNo threshold met the minimum precision; using 0.5.")
        return 0.5

    best_recall, best_precision, risk_threshold = max(candidates, key=lambda item: item[0])
    print(
        f"\nSelected threshold: {risk_threshold:.3f}; "
        f"validation precision={best_precision:.3f}, recall={best_recall:.3f}"
    )
    return float(risk_threshold)


def train_deep_model(X_train, y_train, X_test, y_test):
    """Train an optional neural network, skipping the section if TensorFlow is unavailable."""
    try:
        import tensorflow as tf
    except ImportError:
        print("\nTensorFlow is not installed; skipping deep learning.")
        return None, None

    X_fit, X_validation, y_fit, y_validation = train_test_split(
        X_train, y_train, test_size=0.2,
        random_state=RANDOM_STATE, stratify=y_train
    )
    preprocessor = build_preprocessor(X_fit)
    X_fit_prepared = preprocessor.fit_transform(X_fit)
    X_validation_prepared = preprocessor.transform(X_validation)
    X_test_prepared = preprocessor.transform(X_test)

    if hasattr(X_fit_prepared, "toarray"):
        X_fit_prepared = X_fit_prepared.toarray()
        X_validation_prepared = X_validation_prepared.toarray()
        X_test_prepared = X_test_prepared.toarray()

    tf.keras.utils.set_random_seed(RANDOM_STATE)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(X_fit_prepared.shape[1],)),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(
        optimizer="adam", loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
        ],
    )
    history = model.fit(
        X_fit_prepared, y_fit,
        validation_data=(X_validation_prepared, y_validation),
        epochs=30, batch_size=32,
        callbacks=[tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=4, restore_best_weights=True
        )],
        verbose=1
    )
    risk_probabilities = model.predict(X_test_prepared, verbose=0).ravel()
    risk_predictions = (risk_probabilities >= 0.5).astype(int)
    print("\nDeep-learning test results:")
    print(classification_report(y_test, risk_predictions, zero_division=0))

    make_output_folder()
    plt.figure(figsize=(7, 4))
    plt.plot(history.history["loss"], label="Training loss")
    plt.plot(history.history["val_loss"], label="Validation loss")
    plt.title("Neural network training history")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_FOLDER / "neural_network_training_history.png", dpi=150)
    plt.close()
    return model, history


def load_weekly_engagement(vle_path="studentVle.csv"):
    """Aggregate real VLE clicks if available; otherwise create labelled demo data."""
    if Path(vle_path).exists():
        vle_data = pd.read_csv(vle_path)
        required_columns = {"date", "sum_click"}
        if not required_columns.issubset(vle_data.columns):
            raise ValueError(f"{vle_path} must contain {sorted(required_columns)}.")
        weekly_data = (
            vle_data.groupby(vle_data["date"] // 7)["sum_click"]
            .sum().rename("clicks").reset_index()
            .rename(columns={"date": "week"}).sort_values("week")
        )
        return weekly_data, f"Real VLE data from {vle_path}"

    rng = np.random.default_rng(RANDOM_STATE)
    weeks = np.arange(20)
    base_clicks = 900 + 35 * weeks
    weekly_data = pd.DataFrame({
        "week": weeks,
        "clicks": np.maximum(0, base_clicks + rng.normal(0, 100, len(weeks))).round().astype(int)
    })
    return weekly_data, "Synthetic demonstration data (studentVle.csv was not found)"


def time_series_demo(vle_path="studentVle.csv"):
    """Compare Holt-Winters and ARIMA forecasts on weekly engagement."""
    weekly_data, data_source = load_weekly_engagement(vle_path)
    print(f"\nTime-series data source: {data_source}")
    if len(weekly_data) <
        print("Not enough weekly observations for forecasting.")
        return weekly_data, data_source

    engagement_series = weekly_data.set_index("week")["clicks"].astype(float)
    split_index = max(4, int(len(engagement_series) * 0.8))
    training_series = engagement_series.iloc[:split_index]
    test_series = engagement_series.iloc[split_index:]
    forecasts = {}

    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing
        model = ExponentialSmoothing(training_series, trend="add", seasonal=None).fit()
        forecasts["Holt-Winters"] = model.forecast(len(test_series))
    except Exception as error:
        print(f"Holt-Winters forecast failed: {error}")

    try:
        from statsmodels.tsa.arima.model import ARIMA
        model = ARIMA(training_series, order=(1, 1, 1)).fit()
        forecasts["ARIMA"] = model.forecast(steps=len(test_series))
    except Exception as error:
        print(f"ARIMA forecast failed: {error}")

    forecast_results = []
    for model_name, forecast in forecasts.items():
        mean_absolute_error = np.mean(np.abs(test_series.to_numpy() - forecast.to_numpy()))
        forecast_results.append({
            "model": model_name, "mean_absolute_error": float(mean_absolute_error)
        })

    if forecast_results:
        forecast_table = pd.DataFrame(forecast_results)
        print("\nForecast comparison (lower MAE is better):")
        print(forecast_table.to_string(index=False))
        make_output_folder()
        forecast_table.to_csv(OUTPUT_FOLDER / "time_series_forecast_results.csv", index=False)

    plt.figure(figsize=(8, 4))
    plt.plot(training_series.index, training_series.values, label="Training observations")
    plt.plot(test_series.index, test_series.values, label="Held-out observations")
    for model_name, forecast in forecasts.items():
        plt.plot(test_series.index, forecast.to_numpy(), marker="o", label=model_name)
    plt.title("Weekly VLE engagement forecast")
    plt.xlabel("Week")
    plt.ylabel("Total clicks")
    plt.legend()
    plt.tight_layout()
    make_output_folder()
    plt.savefig(OUTPUT_FOLDER / "weekly_engagement_forecast.png", dpi=150)
    plt.close()

    trend_label = "increasing" if engagement_series.iloc[-1] > engagement_series.iloc[0] else "decreasing or stable"
    print(f"Overall observed engagement trend: {trend_label}")
    return weekly_data, data_source


class RiskChatbot:
    """Small TF-IDF intent matcher for common student-support questions."""

    def __init__(self):
        self.phrases = [
            "How do I know if I am at risk?",
            "How can I improve my engagement?",
            "I have missed assessments",
            "Where can I get academic support?",
            "What does the risk score mean?",
        ]
        self.labels = [
            "risk_explanation", "engagement_advice", "assessment_support",
            "academic_support", "risk_score"
        ]
        self.vectorizer = TfidfVectorizer()
        self.phrase_vectors = self.vectorizer.fit_transform(self.phrases)

    def respond(self, question):
        question_vector = self.vectorizer.transform([question])
        similarities = cosine_similarity(question_vector, self.phrase_vectors)[0]
        intent_index = int(np.argmax(similarities))
        if similarities[intent_index] < 0.08:
            return (
                "I may not understand that question yet. Please contact your lecturer "
                "or student support office for guidance."
            )

        responses = {
            "risk_explanation": (
                "A risk indicator is an early signal for offering support, not a final "
                "judgment about your ability or future."
            ),
            "engagement_advice": (
                "Try setting a weekly study plan, checking course materials regularly, "
                "and contacting your lecturer when you get stuck."
            ),
            "assessment_support": (
                "Check assessment instructions and deadlines, then contact your lecturer "
                "or academic advisor about missed work as soon as possible."
            ),
            "academic_support": (
                "Contact your lecturer, academic advisor, or university student-support "
                "services to discuss the help available to you."
            ),
            "risk_score": (
                "The risk score is a model estimate based on available data. It can be "
                "wrong and should be reviewed alongside the student's circumstances."
            ),
        }
        return responses[self.labels[intent_index]]


def main():
    print("Student Success and Retention System prototype")
    X_train, y_train, X_test, y_test = load_and_prepare(DATA_PATH)
    print(f"Training rows: {len(X_train)} | Test rows: {len(X_test)}")
    print(f"Number of features: {X_train.shape[1]}")

    eda_plots(X_train, y_train)
    trained_models, cv_table = train_ml_models(X_train, y_train)
    best_model_name = cv_table.iloc[0]["model"]
    best_model = trained_models[best_model_name]

    print(f"\nBest baseline model by cross-validation F1: {best_model_name}")
    baseline_results = evaluate(best_model, X_test, y_test, name=best_model_name)
    explain(best_model)
    fairness_check(
        best_model, X_test, y_test,
        group_columns=["gender", "disability", "age_band", "imd_band"]
    )

    tuned_model, best_parameters = tune_best_model(X_train, y_train)
    X_fit, X_validation, y_fit, y_validation = train_test_split(
        X_train, y_train, test_size=0.2,
        random_state=RANDOM_STATE, stratify=y_train
    )
    tuned_model.fit(X_fit, y_fit)
    risk_threshold = choose_threshold(
        tuned_model, X_validation, y_validation, minimum_precision=0.60
    )
    tuned_model.fit(X_train, y_train)
    tuned_results = evaluate(
        tuned_model, X_test, y_test,
        threshold=risk_threshold, name="Tuned Random Forest"
    )
    explain(tuned_model)

    train_deep_model(X_train, y_train, X_test, y_test)
    weekly_data, data_source = time_series_demo("studentVle.csv")

    chatbot = RiskChatbot()
    print("\nStudent support chatbot demonstration:")
    for question in [
        "How do I know if I am at risk?",
        "I have missed assessments",
        "Where can I get academic support?",
    ]:
        print(f"Student: {question}")
        print(f"Chatbot: {chatbot.respond(question)}\n")

    summary = pd.DataFrame([
        {"model": best_model_name, **{key: value for key, value in baseline_results.items() if key != "model"}},
        {"model": "Tuned Random Forest", **{key: value for key, value in tuned_results.items() if key != "model"}},
    ])
    make_output_folder()
    summary.to_csv(OUTPUT_FOLDER / "final_model_comparison.csv", index=False)
    print(f"\nFinished. Output files saved to: {OUTPUT_FOLDER.resolve()}")
    print("Synthetic time-series results are demonstrations, not real findings.")
    print("This prototype must not be used to make decisions about real students.")


if __name__ == "__main__":
    main()
