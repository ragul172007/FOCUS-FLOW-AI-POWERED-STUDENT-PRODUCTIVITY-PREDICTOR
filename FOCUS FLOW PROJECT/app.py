from flask import Flask, render_template, request
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# ==========================================
# LOAD DATASET
# ==========================================

data = pd.read_csv("FOCUS_DATASET.csv")

# Features
X = data[
    [
        "Study_Time",
        "Phone_Usage",
        "Idle_Time"
    ]
]

# Target
y = data["Focus_Level"]

# ==========================================
# ENCODE TARGET
# ==========================================

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# ==========================================
# TRAIN RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y_encoded)

print("FocusFlow Random Forest Model Loaded Successfully")


# ==========================================
# FOCUS SCORE CALCULATION
# ==========================================

def calculate_focus_score(study, phone, idle):

    # Study contribution
    study_score = min(study / 120, 1) * 50

    # Phone contribution
    phone_score = max(0, 30 - phone) / 30 * 30

    # Idle contribution
    idle_score = max(0, 20 - idle) / 20 * 20

    score = study_score + phone_score + idle_score

    score = max(0, min(100, score))

    return round(score)


# ==========================================
# PERSONALIZED RECOMMENDATION
# ==========================================

def get_recommendation(study, phone, idle, result):

    recommendations = []

    # Study time recommendation
    if study < 45:
        recommendations.append(
            "Increase your study time to at least 45 minutes."
        )
    elif study < 90:
        recommendations.append(
            "Try gradually increasing your study sessions toward 90 minutes."
        )
    else:
        recommendations.append(
            "Good study duration. Maintain your current routine."
        )

    # Phone usage recommendation
    if phone > 40:
        recommendations.append(
            "Reduce phone usage during study sessions."
        )
    elif phone > 20:
        recommendations.append(
            "Keep your phone away or use Do Not Disturb while studying."
        )
    else:
        recommendations.append(
            "Your phone usage is well controlled."
        )

    # Idle time recommendation
    if idle > 30:
        recommendations.append(
            "Reduce long idle periods and use short planned breaks."
        )
    elif idle > 15:
        recommendations.append(
            "Try keeping breaks short and structured."
        )
    else:
        recommendations.append(
            "Your idle time is under control."
        )

    # Final result based recommendation
    if result == "Focused":
        recommendations.append(
            "Excellent! Continue your current study habits."
        )
    else:
        recommendations.append(
            "Try a 25-minute focused study session followed by a short break."
        )

    return recommendations


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html",

        prediction="Waiting...",

        confidence=0,

        study=0,

        phone=0,

        idle=0,

        color="#4ea8ff",

        tip="Enter your study details and click Predict.",

        focus_score=0,

        recommendations=[]
    )


# ==========================================
# PREDICTION ROUTE
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ----------------------------------
        # GET USER INPUT
        # ----------------------------------

        study = int(request.form["study_time"])
        phone = int(request.form["phone_usage"])
        idle = int(request.form["idle_time"])

        # ----------------------------------
        # VALIDATE INPUT
        # ----------------------------------

        if study < 0 or phone < 0 or idle < 0:

            return render_template(
                "index.html",
                prediction="Invalid Input",
                confidence=0,
                study=study,
                phone=phone,
                idle=idle,
                color="#ff1744",
                tip="Please enter values greater than or equal to zero.",
                focus_score=0,
                recommendations=[]
            )

        # ----------------------------------
        # CREATE INPUT DATAFRAME
        # ----------------------------------

        sample = pd.DataFrame(
            [[study, phone, idle]],
            columns=[
                "Study_Time",
                "Phone_Usage",
                "Idle_Time"
            ]
        )

        # ----------------------------------
        # ML PREDICTION
        # ----------------------------------

        prediction = model.predict(sample)

        probability = model.predict_proba(sample)

        # Confidence
        confidence = round(
            max(probability[0]) * 100,
            2
        )

        # Convert encoded prediction back to text
        result = encoder.inverse_transform(
            prediction
        )[0]

        # ----------------------------------
        # FOCUS SCORE
        # ----------------------------------

        focus_score = calculate_focus_score(
            study,
            phone,
            idle
        )

        # ----------------------------------
        # PERSONALIZED RECOMMENDATIONS
        # ----------------------------------

        recommendations = get_recommendation(
            study,
            phone,
            idle,
            result
        )

        # ----------------------------------
        # RESULT MESSAGE
        # ----------------------------------

        if result == "Focused":

            color = "#00e676"

            tip = (
                "Excellent! Your study habits indicate "
                "strong focus. Keep phone usage low "
                "and continue your study routine."
            )

        else:

            color = "#ff1744"

            tip = (
                "Your focus level is low. Reduce phone "
                "usage, increase study time, and avoid "
                "long idle periods."
            )

        # ----------------------------------
        # DISPLAY RESULT
        # ----------------------------------

        return render_template(
            "index.html",

            prediction=result,

            confidence=confidence,

            study=study,

            phone=phone,

            idle=idle,

            color=color,

            tip=tip,

            focus_score=focus_score,

            recommendations=recommendations
        )

    except (ValueError, KeyError):

        return render_template(
            "index.html",

            prediction="Invalid Input",

            confidence=0,

            study=0,

            phone=0,

            idle=0,

            color="#ff1744",

            tip="Please enter valid numerical values.",

            focus_score=0,

            recommendations=[]
        )


# ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )