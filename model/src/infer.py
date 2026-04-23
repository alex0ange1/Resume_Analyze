import logging
import os
from pathlib import Path
from typing import Dict, Optional

from keyword_detector import check_all_competencies
from infer_stacking import StackingInference

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


def predict_levels_stacking(
    resume_text: str, competencies_list: list[str]
) -> dict[str, int]:
    """Уровни 0, 1, 2 — как при обучении (мета-модель)."""
    stacker = _get_stacker()
    results = {}
    for comp in competencies_list:
        out = stacker.predict_level(resume_text, comp)
        out_level = out["level"]
        new_level = out_level + 1
        results[comp] = int(new_level)
    return results


# -----------------------------
# Оценка кандидата
# -----------------------------
def evaluate_candidate(
    candidate_levels: Dict[str, int],
    profession_name: str,
    required_skills: Dict[str, int],
) -> dict:
    """
    Оценивает соответствие кандидата профессии

    Args:
        candidate_levels: {skill_name: candidate_level}
        profession_name: название профессии
        required_skills: {skill_name: required_level}

    Returns:
        dict с match_percent и missing_skills
    """
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
# Полная оценка резюме (одна профессия)
# -----------------------------
def full_evaluation(
    resume_text: str, profession: str, required_skills: Optional[Dict[str, int]] = None
) -> dict:
    """
    Оценивает резюме для одной профессии

    Args:
        resume_text: текст резюме
        profession: название профессии
        required_skills: словарь {skill: required_level} (если None, берет из professions_dict)
    """
    if required_skills is None:
        raise ValueError(f"Профессия {profession} не найдена в словаре.")

    competencies = list(required_skills.keys())

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

    evaluation = evaluate_candidate(final_levels, profession, required_skills)

    return {"final_levels": final_levels, "evaluation": evaluation}


# -----------------------------
# Оценка по всем профессиям
# -----------------------------
def evaluate_all_professions(
    resume_text: str,
    target_profession_name: str,
    all_professions: Dict[str, Dict[str, int]],
) -> Dict:
    """
    Оценивает резюме по всем переданным профессиям

    Args:
        resume_text: текст резюме
        target_profession_name: название целевой профессии
        all_professions: словарь {profession_name: {skill_name: required_level}}

    Returns:
        dict с результатами по всем профессиям
    """
    logger.info(f"Evaluating {len(all_professions)} professions for resume")

    # 1. Кэшируем keyword detection (он не зависит от профессии!)
    keyword_hits = check_all_competencies(resume_text)
    logger.info(
        f"Keyword detection completed. Found hits: {sum(keyword_hits.values())} competencies"
    )

    # 2. Получаем все уникальные компетенции с сигналом
    all_competencies_with_signal = [comp for comp, hit in keyword_hits.items() if hit]
    logger.info(
        f"Competencies with keyword signal: {len(all_competencies_with_signal)}"
    )

    # 3. Batch предсказание stacking модели для всех компетенций с сигналом
    model_levels = {}
    if all_competencies_with_signal:
        model_levels = predict_levels_stacking(
            resume_text, all_competencies_with_signal
        )
        logger.info(
            f"Stacking predictions completed for {len(model_levels)} competencies"
        )

    # 4. Оцениваем каждую профессию
    results = {}
    for prof_name, required_skills in all_professions.items():
        competencies = list(required_skills.keys())

        # Формируем финальные уровни для этой профессии
        final_levels = {}
        for comp in competencies:
            if not keyword_hits.get(comp, False):
                final_levels[comp] = 0
            else:
                final_levels[comp] = model_levels.get(comp, 0)

        # Вычисляем процент соответствия
        evaluation = evaluate_candidate(final_levels, prof_name, required_skills)

        results[prof_name] = {
            "match_percent": evaluation["match_percent"],
            "missing_skills": evaluation["missing_skills"],
            "final_levels": final_levels,
        }

    # 5. Находим лучшую профессию
    best_profession = max(results.items(), key=lambda x: x[1]["match_percent"])

    # 6. Определяем, является ли целевая лучшей
    target_match = results.get(target_profession_name, {}).get("match_percent", 0)
    best_match = best_profession[1]["match_percent"]
    is_target_best = target_match >= best_match - 0.01  # с учетом погрешности

    logger.info(f"Target profession '{target_profession_name}': {target_match:.2f}%")
    logger.info(f"Best profession '{best_profession[0]}': {best_match:.2f}%")
    logger.info(f"Is target best: {is_target_best}")

    return {
        "target_result": results.get(target_profession_name),
        "all_results": results,
        "is_target_best": is_target_best,
        "best_profession": best_profession[0]
        if not is_target_best
        else target_profession_name,
    }


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
