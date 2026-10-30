"""Load and prepare student academic data for risk classification."""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from Settings import DATA_PATH, TARGET_COLUMN, RANDOM_STATE

MARK_COLUMNS = ["average_mark", "latest_mark", "mark_change"]


def load_and_prepare(path=DATA_PATH):
    data = pd.read_csv(path).drop_duplicates().copy()

    if TARGET_COLUMN not in data.columns:
        raise ValueError(f"Missing target column: {TARGET_COLUMN}")

    missing_target = data[TARGET_COLUMN].isna().sum()
    if missing_target:
        print(f"Removing {missing_target} records with unknown target labels.")
        data = data.dropna(subset=[TARGET_COLUMN])

    if not set(data[TARGET_COLUMN].unique()).issubset({0, 1}):
        raise ValueError("at_risk must contain only 0 and 1.")

    for column in MARK_COLUMNS:
        indicator = f"{column}_was_missing"
        if column in data.columns and indicator not in data.columns:
            data[indicator] = data[column].isna().astype(int)

    columns_to_remove = [
        "record_key", "student_group",
        "average_mark_was_missing", "latest_mark_was_missing",
        "mark_change_was_missing"
    ]

    X = data.drop(columns=[TARGET_COLUMN] + columns_to_remove, errors="ignore")
    y = data[TARGET_COLUMN].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    print("\nDATA PREPARATION COMPLETED")
    print("-" * 40)
    print(f"Training records: {len(X_train):,}")
    print(f"Testing records: {len(X_test):,}")
    print(f"Number of features: {X_train.shape[1]}")

    return X_train, y_train, X_test, y_test


def build_preprocessor(X):
    numerical = X.select_dtypes(include=np.number).columns.tolist()
    categorical = X.select_dtypes(exclude=np.number).columns.tolist()

    numerical_steps = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler())
    ])

    categorical_steps = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encode", OneHotEncoder(handle_unknown="ignore"))
    ])

    return ColumnTransformer([
        ("num", numerical_steps, numerical),
        ("cat", categorical_steps, categorical)
    ])
