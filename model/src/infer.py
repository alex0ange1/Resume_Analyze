import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from model.data.profession_matrix import professions_dict
from model.src.keyword_detector import check_all_competencies
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Параметры
# -----------------------------
model = None
tokenizer = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# BASE_DIR = Path(__file__).resolve().parent.parent
# OUTPUT_DIR = BASE_DIR / "data" / "rubert-competency"
# device = (
#     torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
# )

# -----------------------------
# Загружаем модель и токенизатор
# -----------------------------
# tokenizer = AutoTokenizer.from_pretrained(OUTPUT_DIR)
# model = AutoModelForSequenceClassification.from_pretrained(OUTPUT_DIR)
# model.to(device)
# model.eval()


import os
from pathlib import Path

def load_model():
    global model, tokenizer
    try:
        base_dir = Path(__file__).resolve().parent.parent  # .../model
        model_path = Path(
            os.getenv("MODEL_PATH", str(base_dir / "data" / "final_model"))
        )

        if not model_path.exists():
            raise FileNotFoundError(f"Model path not found: {model_path}")

        logger.info(f"Loading model from: {model_path}")
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        model.to(device)
        model.eval()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        logger.warning("Model not loaded, using fallback mode")


# -----------------------------
# Функция инференса модели
# -----------------------------
def predict_resume_model(resume_text, competencies_list):
    results = {}
    for comp in competencies_list:
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
            outputs = model(**inputs)
            logits = outputs.logits
            pred_level = int(torch.argmax(logits, dim=-1).item())
            results[comp] = pred_level
    return results


# -----------------------------
# Функция оценки кандидата
# -----------------------------
def evaluate_candidate(
    candidate_levels: dict, profession: str, professions_dict: dict
) -> dict:
    required_skills = professions_dict.get(profession)
    if not required_skills:
        raise ValueError(f"Профессия {profession} не найдена в словаре.")

    total_required = 0
    total_matched = 0
    missing_skills = []

    for skill_name, required_level in required_skills.items():
        candidate_level = candidate_levels.get(skill_name, 0)

        total_required += required_level
        total_matched += min(candidate_level, required_level)

        if candidate_level < required_level:
            missing_skills.append(
                {
                    "name": skill_name,
                    "required_level": required_level,
                    "candidate_level": candidate_level,
                }
            )

    match_percent = (
        (total_matched / total_required * 100) if total_required > 0 else 0.0
    )

    return {"match_percent": match_percent, "missing_skills": missing_skills}


# -----------------------------
# Полная оценка резюме
# -----------------------------
def full_evaluation(resume_text, profession):
    competencies = list(professions_dict[profession].keys())

    # 1. Предсказание модели
    model_levels = predict_resume_model(resume_text, competencies)

    # 2. Проверка ключевых слов
    keyword_levels = {
        comp: int(found)
        for comp, found in check_all_competencies(resume_text).items()
        if comp in competencies
    }

    # 3. Объединяем уровни: берем максимум из модели и keyword detector
    final_levels = {}
    for comp in competencies:
        final_levels[comp] = max(
            model_levels.get(comp, 0),
            keyword_levels.get(comp, 0),
        )

    # 4. Оценка соответствия
    evaluation = evaluate_candidate(final_levels, profession, professions_dict)

    return {"final_levels": final_levels, "evaluation": evaluation}


# -----------------------------
# Пример использования
# -----------------------------
# if __name__ == "__main__":
#     test_resume = "Опыт работы с Python, PyTorch, SQL. Реализовывал модели машинного обучения и обрабатывал данные."
#     profession = "Data Scientist"
#
#     result = full_evaluation(test_resume, profession)
#
#     print("Уровни компетенций:")
#     for comp, level in result["final_levels"].items():
#         print(f"- {comp}: {level}")
#
#     print(f"\nПроцент соответствия: {result['evaluation']['match_percent']:.2f}%")
#     print("Недостающие навыки:")
#     for skill in result['evaluation']['missing_skills']:
#         print(f"- {skill['name']}: требуется {skill['required_level']}, есть {skill['candidate_level']}")

# Загружаем модель при импорте
load_model()
