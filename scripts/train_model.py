from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from app.analyzer import extract_features


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "content_dataset_clean.csv"
MODEL_PATH = BASE_DIR / "models" / "content_classifier.joblib"
METRICS_PATH = BASE_DIR / "models" / "metrics.txt"

NUMERIC_FEATURE_COLUMNS = [
    "char_count",
    "word_count",
    "sentence_count",
    "avg_word_length",
    "avg_sentence_length",
    "exclamation_count",
    "question_count",
    "emotional_word_count",
    "cta_word_count",
    "emotional_ratio",
    "cta_ratio",
]


def build_feature_dataframe(text_series: pd.Series) -> pd.DataFrame:
    rows = []
    for text in text_series:
        feature_row = extract_features(text)
        feature_row["text"] = text
        rows.append(feature_row)
    return pd.DataFrame(rows)


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("tfidf", TfidfVectorizer(max_features=700, ngram_range=(1, 2)), "text"),
            ("num", StandardScaler(), NUMERIC_FEATURE_COLUMNS),
        ]
    )


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    X_raw = df["text"]
    y = df["label"]

    X_features = build_feature_dataframe(X_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X_features,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "linear_svc": LinearSVC(class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            random_state=42,
            class_weight="balanced"
        ),
    }

    results = []
    best_name = None
    best_pipeline = None
    best_f1 = -1.0
    best_report = ""

    for model_name, classifier in models.items():
        pipeline = Pipeline([
            ("preprocessor", build_preprocessor()),
            ("classifier", classifier)
        ])

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="macro")
        report = classification_report(y_test, y_pred)

        results.append({
            "model": model_name,
            "accuracy": acc,
            "macro_f1": f1,
            "report": report
        })

        print(f"\n=== {model_name} ===")
        print(f"Accuracy: {acc:.4f}")
        print(f"Macro F1: {f1:.4f}")
        print(report)

        if f1 > best_f1:
            best_f1 = f1
            best_name = model_name
            best_pipeline = pipeline
            best_report = report

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        f.write(f"Best model: {best_name}\n")
        f.write(f"Best macro F1: {best_f1:.4f}\n\n")

        for result in results:
            f.write(f"=== {result['model']} ===\n")
            f.write(f"Accuracy: {result['accuracy']:.4f}\n")
            f.write(f"Macro F1: {result['macro_f1']:.4f}\n")
            f.write(result["report"])
            f.write("\n\n")

    print(f"\nBest model: {best_name}")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")


if __name__ == "__main__":
    main()