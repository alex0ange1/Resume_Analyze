from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split


SBERT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
RANDOM_STATE = 42


def build_input_text(df: pd.DataFrame) -> pd.Series:
    return "[COMP] " + df["competency"] + " [SEP] " + df["resume_text"]


def load_and_prepare_data(csv_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(csv_path)

    df["resume_text"] = df["resume_text"].fillna("").astype(str).str.strip()
    df["competency"] = df["competency"].fillna("").astype(str).str.strip()
    df = df[(df["resume_text"] != "") & (df["competency"] != "")]
    df = df.drop_duplicates(subset=["competency", "resume_text", "level"]).reset_index(
        drop=True
    )

    df = df[df["level"] != 0].copy()
    df["level"] = df["level"] - 1

    train_df, val_df = train_test_split(
        df,
        test_size=0.1,
        random_state=RANDOM_STATE,
        stratify=df["level"],
    )
    return train_df.reset_index(drop=True), val_df.reset_index(drop=True)


def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    csv_path = data_dir / "competency_500.csv"
    output_dir = data_dir / "final_model_sbert"
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df, val_df = load_and_prepare_data(csv_path)
    x_train_text = build_input_text(train_df).tolist()
    x_val_text = build_input_text(val_df).tolist()
    y_train = train_df["level"].to_numpy(dtype=np.int64)
    y_val = val_df["level"].to_numpy(dtype=np.int64)

    encoder = SentenceTransformer(SBERT_MODEL_NAME)

    x_train_emb = encoder.encode(
        x_train_text,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    x_val_emb = encoder.encode(
        x_val_text,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        multi_class="multinomial",
        solver="lbfgs",
        random_state=RANDOM_STATE,
    )
    clf.fit(x_train_emb, y_train)

    val_pred = clf.predict(x_val_emb)
    val_acc = accuracy_score(y_val, val_pred)
    val_f1 = f1_score(y_val, val_pred, average="macro")

    print(f"[SBERT] val_accuracy={val_acc:.4f}")
    print(f"[SBERT] val_f1_macro={val_f1:.4f}")
    print("[SBERT] classification_report:")
    print(classification_report(y_val, val_pred, digits=4))

    encoder.save(str(output_dir / "encoder"))
    joblib.dump(clf, output_dir / "classifier.joblib")
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "val_accuracy": float(val_acc),
                "val_f1_macro": float(val_f1),
                "num_train": int(len(train_df)),
                "num_val": int(len(val_df)),
                "sbert_model_name": SBERT_MODEL_NAME,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"SBERT encoder saved to: {output_dir / 'encoder'}")
    print(f"SBERT classifier saved to: {output_dir / 'classifier.joblib'}")


if __name__ == "__main__":
    main()
