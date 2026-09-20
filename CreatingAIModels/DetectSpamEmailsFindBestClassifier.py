# This script demonstrates how to use GridSearchCV to find the best hyperparameters for multiple classifiers to detect spam emails. It evaluates the multiple models using accuracy, precision, recall, and F1 score.

from os import write

import pandas as pd
import pickle

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

# load data
data = pd.read_csv("dataset.csv")

# features and target
X = data.iloc[:, 1:-1].astype(float)
y = data["Prediction"].astype(int)

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# define models + parameter grids
models = {
    "DecisionTree": (
        DecisionTreeClassifier(random_state=42),
        {
            "max_depth": [None, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4]
        }
    ),
    "RandomForest": (
        RandomForestClassifier(random_state=42),
        {
            "n_estimators": [100, 200, 300],
            "max_depth": [None, 5, 10, 15],
            "min_samples_split": [2, 5, 10]
        }
    ),
    "LogisticRegression": (
        LogisticRegression(max_iter=1000, random_state=42),
        {
             "C": [0.01, 0.1, 1, 10],
             "solver": ["liblinear", "lbfgs"]
         }
    ),
    "SVC": (
        SVC(random_state=42),
        {
            "C": [0.1, 1, 10],
            "kernel": ["linear", "rbf"],
            "gamma": ["scale", "auto"]
        }
    )
}

best_result = None

for name, (model, param_grid) in models.items():
    grid = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        scoring="f1",   # use "recall" if you want to detect spam more aggressively
        cv=5,
        n_jobs=-1
    )

    grid.fit(X_train, y_train)

    y_pred = grid.best_estimator_.predict(X_test)

    metrics = {
        "model": name,
        "best_params": grid.best_params_,
        "best_cv_score": grid.best_score_,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
    }

    print(f"\nModel: {name}")
    print("Best params:", grid.best_params_)
    print("CV F1:", grid.best_score_)
    print("Accuracy:", metrics["accuracy"])
    print("Precision:", metrics["precision"])
    print("Recall:", metrics["recall"])
    print("F1:", metrics["f1"])

    if best_result is None or metrics["f1"] > best_result["f1"]:
        best_result = metrics
        best_model = grid.best_estimator_

# save the best model
with write("best_spam_classifier.pkl", "wb") as f:
    pickle.dump(best_model, f)

print("\nBest model overall:")
print(best_result)