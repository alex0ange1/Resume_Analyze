from typing import Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.depends import get_current_user

ml_router = APIRouter()


class ResumeEvaluationRequest(BaseModel):
    resume_text: str
    profession: str


class MLServiceResponse(BaseModel):
    final_levels: Dict[str, int]
    evaluation: dict


ML_SERVICE_URL = "http://ml_service:8000"


@ml_router.post(
    "/evaluate-resume",
    response_model=MLServiceResponse,
    # dependencies=[Depends(get_current_user)],
)
async def evaluate_resume(request: ResumeEvaluationRequest):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ML_SERVICE_URL}/evaluate-resume",
                json=request.model_dump(),
                timeout=30.0,
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="ML service unavailable",
                )

            return response.json()

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML service connection error: {str(e)}",
        )
