import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any

# Импортируем функцию оценки из вашего существующего кода
from .infer import full_evaluation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ML Model Service",
    description="Сервис для анализа резюме с помощью ML модели",
    version="1.0.0",
)


class ResumeEvaluationRequest(BaseModel):
    resume_text: str
    profession: str


class MissingSkill(BaseModel):
    name: str
    required_level: int
    candidate_level: int


class EvaluationResponse(BaseModel):
    match_percent: float
    missing_skills: List[MissingSkill]


class MLServiceResponse(BaseModel):
    final_levels: Dict[str, int]
    evaluation: EvaluationResponse


@app.post("/evaluate-resume", response_model=MLServiceResponse)
async def evaluate_resume(request: ResumeEvaluationRequest):
    try:
        logger.info(f"Evaluating resume for profession: {request.profession}")

        # Используем существующую функцию full_evaluation
        result = full_evaluation(request.resume_text, request.profession)

        # Преобразуем missing_skills для Pydantic
        evaluation_response = EvaluationResponse(
            match_percent=result["evaluation"]["match_percent"],
            missing_skills=[
                MissingSkill(**skill)
                for skill in result["evaluation"]["missing_skills"]
            ],
        )

        return MLServiceResponse(
            final_levels=result["final_levels"], evaluation=evaluation_response
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error evaluating resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml_model_service"}


@app.get("/professions")
async def get_available_professions():
    """Возвращает список доступных профессий"""
    from .infer import professions_dict

    return {"available_professions": list(professions_dict.keys())}
