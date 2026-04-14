from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from app.analyzer import extract_features


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "content_classifier.joblib"

model = None


def load_model():
    global model
    if model is None:
        model = joblib.load(MODEL_PATH)
    return model


def build_input_dataframe(text: str) -> pd.DataFrame:
    features = extract_features(text)
    features["text"] = text
    return pd.DataFrame([features])


def _normalize_decision_scores(scores: np.ndarray, classes: list[str]) -> dict[str, float]:
    scores = np.asarray(scores, dtype=float)
    exp_scores = np.exp(scores - np.max(scores))
    probs = exp_scores / exp_scores.sum()

    return {
        str(cls): float(prob)
        for cls, prob in zip(classes, probs)
    }


def predict(text: str) -> dict:
    clf = load_model()
    df = build_input_dataframe(text)

    prediction = clf.predict(df)[0]
    classes = list(clf.classes_)

    if hasattr(clf, "predict_proba"):
        probabilities = clf.predict_proba(df)[0]
        prob_dict = {
            str(cls): float(prob)
            for cls, prob in zip(classes, probabilities)
        }
    elif hasattr(clf, "decision_function"):
        decision_scores = clf.decision_function(df)[0]
        prob_dict = _normalize_decision_scores(decision_scores, classes)
    else:
        prob_value = round(1.0 / len(classes), 3)
        prob_dict = {str(cls): prob_value for cls in classes}

    return {
        "predicted_class": str(prediction),
        "probabilities": prob_dict
    }