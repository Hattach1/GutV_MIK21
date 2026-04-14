from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "content_dataset.csv"
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "content_dataset_clean.csv"


def clean_text(text: str) -> str:
    return " ".join(str(text).strip().split())


def preprocess_dataset() -> None:
    df = pd.read_csv(RAW_DATA_PATH)

    df = df.dropna(subset=["text", "label"]).copy()
    df["text"] = df["text"].astype(str).apply(clean_text)
    df["label"] = df["label"].astype(str).str.strip().str.lower()

    valid_labels = {"low", "medium", "high"}
    df = df[df["label"].isin(valid_labels)]

    df = df[df["text"].str.len() >= 5]
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"Saved cleaned dataset to: {PROCESSED_DATA_PATH}")
    print(f"Rows: {len(df)}")
    print(df["label"].value_counts())


if __name__ == "__main__":
    preprocess_dataset()