import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# ==========================================
# 1. LOAD DATASET
# ==========================================

data = pd.read_csv("FOCUS_DATASET.csv")

print("\n========================================")
print("       FOCUS FLOW ML MODEL")
print("========================================")

print("\nDataset loaded successfully!")
print("Total Records:", len(data))

# ==========================================
# 2. DISPLAY DATASET INFORMATION
# ==========================================

print("\nDataset Columns:")
print(data.columns.tolist())

print("\nFocus Level Distribution:")
print(data["Focus_Level"].value_counts())

# ==========================================
# 3. DATA PREPROCESSING
# ==========================================

# Remove missing values
data = data.dropna()

# Encode Focus_Level
encoder = LabelEncoder()

data["Focus_Level"] = encoder.fit_transform(
    data["Focus_Level"]
)

# ==========================================
# 4. SELECT FEATURES AND TARGET
# ==========================================

X = data[
    [
        "Study_Time",
        "Phone_Usage",
        "Idle_Time"
    ]
]

y = data["Focus_Level"]

# ==========================================
# 5. SPLIT DATA
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))

# ==========================================
# 6. CREATE RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# ==========================================
# 7. TRAIN MODEL
# ==========================================

model.fit(X_train, y_train)

print("\nRandom Forest model trained successfully!")
# ==========================================
# 6A. 5-FOLD CROSS-VALIDATION
# ==========================================

cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=5,
    scoring="accuracy"
)

print("\n========================================")
print("       5-FOLD CROSS-VALIDATION")
print("========================================")

for i, score in enumerate(cv_scores, start=1):
    print(f"Fold {i} Accuracy : {score * 100:.2f}%")

print(
    f"\nAverage CV Accuracy : "
    f"{cv_scores.mean() * 100:.2f}%"
)

print(
    f"Standard Deviation  : "
    f"{cv_scores.std() * 100:.2f}%"
)

# ==========================================
# 8. MAKE PREDICTIONS
# ==========================================

y_pred = model.predict(X_test)

# ==========================================
# 9. MODEL EVALUATION
# ==========================================

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

print("\n========================================")
print("          MODEL PERFORMANCE")
print("========================================")

print(f"Accuracy  : {accuracy * 100:.2f}%")
print(f"Precision : {precision * 100:.2f}%")
print(f"Recall    : {recall * 100:.2f}%")
print(f"F1 Score  : {f1 * 100:.2f}%")

# ==========================================
# 10. CONFUSION MATRIX
# ==========================================

cm = confusion_matrix(y_test, y_pred)

print("\n========================================")
print("          CONFUSION MATRIX")
print("========================================")

print(cm)

# ==========================================
# 11. CLASSIFICATION REPORT
# ==========================================

print("\n========================================")
print("       CLASSIFICATION REPORT")
print("========================================")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=encoder.classes_,
        zero_division=0
    )
)

# ==========================================
# 12. FEATURE IMPORTANCE
# ==========================================

importance = model.feature_importances_

print("\n========================================")
print("        FEATURE IMPORTANCE")
print("========================================")

for feature, value in zip(X.columns, importance):

    print(
        f"{feature:15s}: {value * 100:.2f}%"
    )

# ==========================================
# 13. TEST NEW STUDENT
# ==========================================

new_student = pd.DataFrame(
    [[100, 15, 5]],
    columns=[
        "Study_Time",
        "Phone_Usage",
        "Idle_Time"
    ]
)

prediction = model.predict(new_student)

probability = model.predict_proba(new_student)

result = encoder.inverse_transform(prediction)[0]

confidence = max(probability[0]) * 100

print("\n========================================")
print("          SAMPLE PREDICTION")
print("========================================")

print("Study Time  : 100 minutes")
print("Phone Usage : 15 minutes")
print("Idle Time   : 5 minutes")

print("\nPrediction  :", result)
print(f"Confidence  : {confidence:.2f}%")

print("\n========================================")
print("        TRAINING COMPLETED")
print("========================================")