from pathlib import Path

import joblib
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class StackingInference:
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent
        data_dir = self.base_dir / "data"

        rubert_dir = data_dir / "final_model"
        sbert_dir = data_dir / "final_model_sbert"
        meta_dir = data_dir / "final_model_meta"

        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

        self.rubert_tokenizer = AutoTokenizer.from_pretrained(rubert_dir)
        self.rubert_model = AutoModelForSequenceClassification.from_pretrained(rubert_dir).to(
            self.device
        )
        self.rubert_model.eval()

        self.sbert_encoder = SentenceTransformer(str(sbert_dir / "encoder"))
        self.sbert_clf = joblib.load(sbert_dir / "classifier.joblib")
        self.meta_clf = joblib.load(meta_dir / "logreg_meta.joblib")

    def _rubert_proba(self, resume_text: str, competency: str) -> np.ndarray:
        inputs = self.rubert_tokenizer(
            resume_text,
            competency,
            truncation=True,
            padding="max_length",
            max_length=256,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            logits = self.rubert_model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze(0).cpu().numpy()
        return probs

    def _sbert_proba(self, resume_text: str, competency: str) -> np.ndarray:
        text = f"[COMP] {competency} [SEP] {resume_text}"
        emb = self.sbert_encoder.encode(
            [text], convert_to_numpy=True, normalize_embeddings=True
        )
        probs = self.sbert_clf.predict_proba(emb)[0]
        return probs

    def predict_level(self, resume_text: str, competency: str) -> dict:
        rubert_p = self._rubert_proba(resume_text, competency)
        sbert_p = self._sbert_proba(resume_text, competency)
        meta_features = np.hstack([rubert_p, sbert_p]).reshape(1, -1)

        final_level = int(self.meta_clf.predict(meta_features)[0])
        final_probs = self.meta_clf.predict_proba(meta_features)[0].tolist()

        return {
            "level": final_level,
            "meta_probs": final_probs,
            "rubert_probs": rubert_p.tolist(),
            "sbert_probs": sbert_p.tolist(),
        }
