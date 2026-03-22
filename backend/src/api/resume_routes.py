import logging
import grpc
import tempfile
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from api.depends import get_current_user, ml_client, database, profession_repo
from services.resume_parser import ResumeParser

logger = logging.getLogger(__name__)

resume_router = APIRouter()


@resume_router.post(
    "/resumes/analyze",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def analyze_resume(
    file: UploadFile = File(..., description="Файл с резюме (pdf, docx, txt)"),
    profession: str = Form(..., description="Название профессии"),
):
    allowed_extensions = {".pdf", ".docx", ".txt"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}",
        )

    try:
        async with database.session() as session:
            profession_obj = await profession_repo.get_profession_by_name(
                session=session, name=profession
            )

            if not profession_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Профессия '{profession}' не найдена в базе данных. Доступные профессии можно посмотреть в разделе 'Профессии'.",
                )

            logger.info(f"Profession '{profession}' found with ID: {profession_obj.id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking profession existence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при проверке профессии: {str(e)}",
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        resume_text = ResumeParser.parse(tmp_path, file_ext)

        logger.info(f"Sending resume to ML service for profession: {profession}")

        ml_response = await ml_client.evaluate_resume(
            resume_text=resume_text, profession=profession
        )

        response = {
            "profession": profession,
            "match_percent": ml_response.evaluation.match_percent,
            "final_levels": dict(ml_response.final_levels),
            "missing_skills": [
                {
                    "name": skill.name,
                    "required_level": skill.required_level,
                    "candidate_level": skill.candidate_level,
                }
                for skill in ml_response.evaluation.missing_skills
            ],
        }

        logger.info(
            f"Analysis completed. Match: {ml_response.evaluation.match_percent:.2f}%"
        )

        return response

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.code()} - {e.details()}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML service unavailable: {e.details()}",
        )
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}",
        )
    finally:
        if "tmp_path" in locals():
            os.unlink(tmp_path)
