# This script demonstrates how to use a Decision Tree Classifier to detect spam emails. It evaluates the model using accuracy, precision, recall, and F1 score for different max_depth values. It uses trial and error method to find the best max_depth for the Decision Tree Classifier.

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# dataset.csv should contain an email/message column and a spam/label column.
data2 = pd.read_csv("dataset.csv")
data = data2

# print(data.info())
# print(data.columns)


# extract features and target
X = data2.iloc[:, 1:-1].astype(float)   # all word columns except Email No. and Prediction
y = data2["Prediction"].astype(int)     # target column

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# model -> Decision Tree Classifier | max_depth=5
model = DecisionTreeClassifier(random_state=42, max_depth=5)
model.fit(X_train, y_train)

# predict
y_pred = model.predict(X_test)

# metrics
print("---------Decision Tree Classifier | max_depth=5---------")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, zero_division=0))
print("Recall:", recall_score(y_test, y_pred, zero_division=0))
print("F1:", f1_score(y_test, y_pred, zero_division=0))
print("--------------------------------------------------------")

# model -> Decision Tree Classifier | max_depth=6
model = DecisionTreeClassifier(random_state=42, max_depth=6)
model.fit(X_train, y_train)

# predict
y_pred = model.predict(X_test)

# metrics
print("---------Decision Tree Classifier | max_depth=6---------")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, zero_division=0))
print("Recall:", recall_score(y_test, y_pred, zero_division=0))
print("F1:", f1_score(y_test, y_pred, zero_division=0))
print("--------------------------------------------------------")

# model -> Decision Tree Classifier | max_depth=7
model = DecisionTreeClassifier(random_state=42, max_depth=7)
model.fit(X_train, y_train)

# predict
y_pred = model.predict(X_test)

# metrics
print("---------Decision Tree Classifier | max_depth=7---------")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, zero_division=0))
print("Recall:", recall_score(y_test, y_pred, zero_division=0))
print("F1:", f1_score(y_test, y_pred, zero_division=0))
print("--------------------------------------------------------")

# model -> Decision Tree Classifier | max_depth=8
model = DecisionTreeClassifier(random_state=42, max_depth=8)
model.fit(X_train, y_train)

# predict
y_pred = model.predict(X_test)

# metrics
print("---------Decision Tree Classifier | max_depth=8---------")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, zero_division=0))
print("Recall:", recall_score(y_test, y_pred, zero_division=0))
print("F1:", f1_score(y_test, y_pred, zero_division=0))
print("--------------------------------------------------------")

# model -> Decision Tree Classifier | max_depth=9
model = DecisionTreeClassifier(random_state=42, max_depth=9)
model.fit(X_train, y_train)

# predict
y_pred = model.predict(X_test)

# metrics
print("---------Decision Tree Classifier | max_depth=9---------")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred, zero_division=0))
print("Recall:", recall_score(y_test, y_pred, zero_division=0))
print("F1:", f1_score(y_test, y_pred, zero_division=0))
print("--------------------------------------------------------")