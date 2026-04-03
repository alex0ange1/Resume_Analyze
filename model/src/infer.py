import logging
import os
from pathlib import Path

from model.data.profession_matrix import professions_dict
from model.src.keyword_detector import check_all_competencies
from model.src.infer_stacking import StackingInference

logger = logging.getLogger(__name__)

# -----------------------------
# Stacking: ruBERT + SBERT + meta LogisticRegression
# -----------------------------
_stacker: StackingInference | None = None


def _get_stacker() -> StackingInference:
    global _stacker
    if _stacker is None:
        base_dir = Path(__file__).resolve().parent.parent
        if os.getenv("MODEL_BASE_DIR"):
            base_dir = Path(os.environ["MODEL_BASE_DIR"])
        _stacker = StackingInference(base_dir=base_dir)
        logger.info("StackingInference loaded (ruBERT + SBERT + meta)")
    return _stacker


def predict_levels_stacking(resume_text: str, competencies_list: list[str]) -> dict[str, int]:
    """Уровни 0, 1, 2 — как при обучении (мета-модель)."""
    stacker = _get_stacker()
    results = {}
    for comp in competencies_list:
        out = stacker.predict_level(resume_text, comp)
        results[comp] = int(out["level"])
    return results


# -----------------------------
# Оценка кандидата
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
def full_evaluation(resume_text: str, profession: str):
    competencies = list(professions_dict[profession].keys())

    # 1. Keyword: нет упоминания → 0 (stacking не вызываем).
    keyword_hits = check_all_competencies(resume_text)

    # 2. Stacking только там, где keyword дал сигнал (уровни 0, 1, 2).
    comps_with_signal = [c for c in competencies if keyword_hits.get(c, False)]
    model_levels = (
        predict_levels_stacking(resume_text, comps_with_signal)
        if comps_with_signal
        else {}
    )

    final_levels = {}
    for comp in competencies:
        if not keyword_hits.get(comp, False):
            final_levels[comp] = 0
        else:
            final_levels[comp] = model_levels.get(comp, 0)

    evaluation = evaluate_candidate(final_levels, profession, professions_dict)

    return {"final_levels": final_levels, "evaluation": evaluation}


if __name__ == "__main__":
    test_resume = "Опыт работы с Python, PyTorch, SQL. Реализовывал модели машинного обучения и обрабатывал данные."
    profession = "Data Scientist"

    result = full_evaluation(test_resume, profession)

    print("Уровни компетенций:")
    for comp, level in result["final_levels"].items():
        print(f"- {comp}: {level}")

    print(f"\nПроцент соответствия: {result['evaluation']['match_percent']:.2f}%")
    print("Недостающие навыки:")
    for skill in result["evaluation"]["missing_skills"]:
        print(
            f"- {skill['name']}: требуется {skill['required_level']}, есть {skill['candidate_level']}"
        )
