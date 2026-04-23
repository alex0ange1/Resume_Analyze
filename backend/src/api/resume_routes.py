import logging
import grpc
import tempfile
import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from api.depends import (
    get_current_user,
    ml_client,
    database,
    profession_repo,
    competence_repo,
)
from services.resume_parser import ResumeParser
from proto import ml_service_pb2

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
            all_professions_db = await profession_repo.get_all_professions(
                session=session
            )

            if not all_professions_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="В базе данных нет ни одной профессии. Сначала создайте профессии.",
                )

            target_profession_obj = None
            for prof in all_professions_db:
                if prof.name.lower() == profession.lower():
                    target_profession_obj = prof
                    break

            if not target_profession_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Профессия '{profession}' не найдена в базе данных. Доступные профессии можно посмотреть в разделе 'Профессии'.",
                )

            logger.info(
                f"Target profession '{profession}' found with ID: {target_profession_obj.id}"
            )
            logger.info(f"Total professions in DB: {len(all_professions_db)}")

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
        logger.info(
            f"Resume parsed successfully. Text length: {len(resume_text)} characters"
        )

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing resume: {str(e)}",
        )
    finally:
        if "tmp_path" in locals():
            os.unlink(tmp_path)

    try:
        async with database.session() as session:
            target_profession_pb = await _convert_profession_to_protobuf(
                target_profession_obj, session, competence_repo
            )

            all_professions_pb = []
            for prof in all_professions_db:
                pb_prof = await _convert_profession_to_protobuf(
                    prof, session, competence_repo
                )
                all_professions_pb.append(pb_prof)

        logger.info(f"Sending {len(all_professions_pb)} professions to ML service")

    except Exception as e:
        logger.error(f"Error preparing data for ML service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка подготовки данных: {str(e)}",
        )

    try:
        ml_response = await ml_client.evaluate_resume(
            resume_text=resume_text,
            target_profession=target_profession_pb,
            all_professions=all_professions_pb,
        )

        logger.info(
            f"ML service response received. Is target best: {ml_response.is_target_best}"
        )

    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.code()} - {e.details()}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"ML service unavailable: {e.details()}",
        )
    except Exception as e:
        logger.error(f"Error calling ML service: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing resume: {str(e)}",
        )

    try:
        target_result = _convert_profession_match_to_dict(ml_response.target_result)

        response = {
            "profession": profession,
            "match_percent": target_result["match_percent"],
            "final_levels": target_result["final_levels"],
            "missing_skills": target_result["missing_skills"],
        }

        best_profession = ml_response.best_profession
        if not ml_response.is_target_best and ml_response.alternative_professions:
            alternatives = []
            for alt in ml_response.alternative_professions[:3]:
                alt_dict = _convert_profession_match_to_dict(alt)
                alternatives.append(
                    {
                        "profession": alt_dict["name"],
                        "match_percent": alt_dict["match_percent"],
                    }
                )

            response["recommendation"] = {
                "is_target_best": False,
                "better_profession": best_profession,
                "alternative_professions": alternatives,
                "message": f"Вы хорошо подходите на позицию '{best_profession}' (совпадение {_get_match_percent_for_profession(ml_response, best_profession):.1f}%)",
            }

            logger.info(f"Adding recommendation: better profession '{best_profession}'")
        else:
            response["recommendation"] = {
                "is_target_best": True,
                "message": f"Позиция: '{profession}' (совпадение {_get_match_percent_for_profession(ml_response, best_profession):.1f}%)",
            }

        logger.info("Response prepared successfully")
        return response

    except Exception as e:
        logger.error(f"Error formatting response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error formatting response: {str(e)}",
        )


async def _convert_profession_to_protobuf(profession, session, competence_repo):
    """
    Конвертирует профессию из БД в protobuf формат с названиями компетенций
    """
    pb_profession = ml_service_pb2.Profession()
    pb_profession.name = profession.name

    for comp_id, required_level in profession.competencies.items():
        try:
            competence = await competence_repo.get_competence_by_id(session, comp_id)
            competency = pb_profession.competencies.add()
            competency.name = competence.name
            competency.required_level = required_level
        except Exception as e:
            logger.warning(
                f"Competence {comp_id} not found for profession {profession.name}: {str(e)}"
            )
            continue

    return pb_profession


def _convert_profession_match_to_dict(profession_match) -> dict:
    """
    Конвертирует protobuf ProfessionMatch в словарь

    Args:
        profession_match: ProfessionMatch protobuf объект

    Returns:
        dict с результатами анализа
    """
    missing_skills = []
    for skill in profession_match.missing_skills:
        missing_skills.append(
            {
                "name": skill.name,
                "required_level": skill.required_level,
                "candidate_level": skill.candidate_level,
            }
        )

    final_levels = dict(profession_match.final_levels)

    return {
        "name": profession_match.name,
        "match_percent": profession_match.match_percent,
        "final_levels": final_levels,
        "missing_skills": missing_skills,
    }


def _get_match_percent_for_profession(ml_response, profession_name: str) -> float:
    """
    Получает процент соответствия для конкретной профессии из ответа ML
    """
    if ml_response.target_result.name == profession_name:
        return ml_response.target_result.match_percent

    for alt in ml_response.alternative_professions:
        if alt.name == profession_name:
            return alt.match_percent

    return 0.0
