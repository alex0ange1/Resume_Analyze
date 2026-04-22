from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer


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


def rubert_predict_proba(
    model, tokenizer, resume_texts: list[str], competencies: list[str], device: torch.device
) -> np.ndarray:
    model.eval()
    probs = []
    for resume_text, comp in tqdm(
        zip(resume_texts, competencies),
        total=len(resume_texts),
        desc="ruBERT predict",
    ):
        inputs = tokenizer(
            resume_text,
            comp,
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = model(**inputs).logits
            p = torch.softmax(logits, dim=-1).squeeze(0).cpu().numpy()
        probs.append(p)
    return np.asarray(probs)


def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    csv_path = data_dir / "competency_500.csv"

    rubert_dir = data_dir / "final_model"
    sbert_dir = data_dir / "final_model_sbert"
    meta_dir = data_dir / "final_model_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    if not rubert_dir.exists():
        raise FileNotFoundError(f"ruBERT model dir not found: {rubert_dir}")
    if not (sbert_dir / "encoder").exists() or not (sbert_dir / "classifier.joblib").exists():
        raise FileNotFoundError(
            f"SBERT artifacts not found in: {sbert_dir}. Run train_sbert.py first."
        )

    train_df, val_df = load_and_prepare_data(csv_path)

    y_train = train_df["level"].to_numpy(dtype=np.int64)
    y_val = val_df["level"].to_numpy(dtype=np.int64)

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    rubert_tokenizer = AutoTokenizer.from_pretrained(rubert_dir)
    rubert_model = AutoModelForSequenceClassification.from_pretrained(rubert_dir).to(device)

    x_train_rubert = rubert_predict_proba(
        rubert_model,
        rubert_tokenizer,
        train_df["resume_text"].tolist(),
        train_df["competency"].tolist(),
        device,
    )
    x_val_rubert = rubert_predict_proba(
        rubert_model,
        rubert_tokenizer,
        val_df["resume_text"].tolist(),
        val_df["competency"].tolist(),
        device,
    )

    sbert_encoder = SentenceTransformer(str(sbert_dir / "encoder"))
    sbert_clf = joblib.load(sbert_dir / "classifier.joblib")

    x_train_text = build_input_text(train_df).tolist()
    x_val_text = build_input_text(val_df).tolist()

    x_train_emb = sbert_encoder.encode(
        x_train_text,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    x_val_emb = sbert_encoder.encode(
        x_val_text,
        batch_size=64,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    x_train_sbert = sbert_clf.predict_proba(x_train_emb)
    x_val_sbert = sbert_clf.predict_proba(x_val_emb)

    x_train_meta = np.hstack([x_train_rubert, x_train_sbert])
    x_val_meta = np.hstack([x_val_rubert, x_val_sbert])

    meta_clf = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        multi_class="multinomial",
        solver="lbfgs",
        random_state=RANDOM_STATE,
    )
    meta_clf.fit(x_train_meta, y_train)

    val_pred = meta_clf.predict(x_val_meta)
    val_acc = accuracy_score(y_val, val_pred)
    val_f1 = f1_score(y_val, val_pred, average="macro")

    print(f"[STACKING] val_accuracy={val_acc:.4f}")
    print(f"[STACKING] val_f1_macro={val_f1:.4f}")
    print("[STACKING] classification_report:")
    print(classification_report(y_val, val_pred, digits=4))

    joblib.dump(meta_clf, meta_dir / "logreg_meta.joblib")
    with (meta_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "val_accuracy": float(val_acc),
                "val_f1_macro": float(val_f1),
                "num_train": int(len(train_df)),
                "num_val": int(len(val_df)),
                "features": [
                    "rubert_p0",
                    "rubert_p1",
                    "rubert_p2",
                    "sbert_p0",
                    "sbert_p1",
                    "sbert_p2",
                ],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Meta model saved to: {meta_dir / 'logreg_meta.joblib'}")


if __name__ == "__main__":
    main()
