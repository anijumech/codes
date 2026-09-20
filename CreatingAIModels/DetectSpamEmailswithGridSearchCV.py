# This script demonstrates how to use GridSearchCV to find the best hyperparameters for a Decision Tree Classifier to detect spam emails. It evaluates the model using accuracy, precision, recall, and F1 score.

import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle

# load data
data = pd.read_csv("dataset.csv")

# features and target
X = data.iloc[:, 1:-1].astype(float)
y = data["Prediction"].astype(int)

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# search for best max_depth
param_grid = {
    "max_depth": range(6, 10)
}

model = DecisionTreeClassifier(random_state=42)

grid = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    scoring="f1",       # or "recall" if catching spam is more important
    cv=5,
    n_jobs=-1
)

grid.fit(X_train, y_train)

best_model = grid.best_estimator_
y_pred = best_model.predict(X_test)

print("Best max_depth:", grid.best_params_["max_depth"])
print("Best CV F1:", grid.best_score_)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, zero_division=0))
print("Recall:", recall_score(y_test, y_pred, zero_division=0))
print("F1:", f1_score(y_test, y_pred, zero_division=0))

with open("best_spam_classifier.pkl", "wb") as f:
    pickle.dump(best_model, f)