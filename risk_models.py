"""The ONLY two predictive models: Logistic Regression and Random Forest."""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.pipeline import Pipeline
from preparation import build_preprocessor
from Settings import OUTPUT_FOLDER, RANDOM_STATE, make_output_folder

def run_risk_models(X_train, y_train, X_test, y_test):
    models = {
        'Logistic Regression': LogisticRegression(max_iter=2000, class_weight='balanced', random_state=RANDOM_STATE),
        'Random Forest': RandomForestClassifier(n_estimators=150, min_samples_leaf=3, class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1),
    }
    results = []
    make_output_folder()
    for name, classifier in models.items():
        model = Pipeline([('preprocess', build_preprocessor(X_train)), ('classifier', classifier)])
        model.fit(X_train, y_train)
        predicted = model.predict(X_test)
        probability = model.predict_proba(X_test)[:, 1]
        row = {'model': name, 'accuracy': accuracy_score(y_test, predicted),
               'precision': precision_score(y_test, predicted, zero_division=0),
               'recall': recall_score(y_test, predicted, zero_division=0),
               'f1': f1_score(y_test, predicted, zero_division=0),
               'roc_auc': roc_auc_score(y_test, probability)}
        results.append(row)
        print(f'\n{name}:', row)
        print('Confusion matrix (rows actual, columns predicted):\n', confusion_matrix(y_test, predicted))
    comparison = pd.DataFrame(results)
    comparison.to_csv(OUTPUT_FOLDER / 'model_comparison.csv', index=False)
    print('\nModel comparison:\n', comparison.to_string(index=False))
    print('NOTE: These are holdout scores, not evidence of deployment readiness.')
    return comparison
