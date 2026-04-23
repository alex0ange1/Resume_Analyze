import asyncio
import logging
from typing import Dict
import grpc
from concurrent import futures

from proto import ml_service_pb2, ml_service_pb2_grpc
from infer import evaluate_all_professions

logger = logging.getLogger(__name__)


class ResumeAnalyzerServicer(ml_service_pb2_grpc.ResumeAnalyzerServicer):
    async def EvaluateResume(
        self, request: ml_service_pb2.ResumeRequest, context: grpc.aio.ServicerContext
    ) -> ml_service_pb2.ResumeResponse:
        """
        Анализирует резюме по всем переданным профессиям
        """
        try:
            resume_text = request.resume_text
            target_profession_name = request.target_profession.name

            logger.info(
                f"Evaluating resume for target profession: {target_profession_name}"
            )
            logger.info(
                f"Total professions to evaluate: {len(request.all_professions)}"
            )

            # 1. Конвертируем protobuf в словарь для всех профессий
            all_professions: Dict[str, Dict[str, int]] = {}

            for prof in request.all_professions:
                competencies_dict = {}
                for comp in prof.competencies:
                    competencies_dict[comp.name] = comp.required_level
                all_professions[prof.name] = competencies_dict

            # Добавляем целевую профессию, если ее нет в списке (на всякий случай)
            if target_profession_name not in all_professions:
                target_competencies = {}
                for comp in request.target_profession.competencies:
                    target_competencies[comp.name] = comp.required_level
                all_professions[target_profession_name] = target_competencies

            # 2. Вызываем массовую оценку
            evaluation_result = evaluate_all_professions(
                resume_text=resume_text,
                target_profession_name=target_profession_name,
                all_professions=all_professions,
            )

            # 3. Формируем ответ
            target_result = evaluation_result["target_result"]
            if target_result is None:
                raise ValueError(
                    f"Target profession '{target_profession_name}' not found in results"
                )

            # Создаем ProfessionMatch для целевой профессии
            target_pb = self._create_profession_match(
                target_profession_name, target_result
            )

            # Создаем альтернативы (все кроме целевой, отсортированные по убыванию)
            alternatives = []
            for prof_name, result in evaluation_result["all_results"].items():
                if prof_name == target_profession_name:
                    continue
                alternatives.append(self._create_profession_match(prof_name, result))

            # Сортируем по match_percent
            alternatives.sort(key=lambda x: x.match_percent, reverse=True)

            # Берем топ-3
            top_alternatives = alternatives[:3]

            response = ml_service_pb2.ResumeResponse(
                target_result=target_pb,
                alternative_professions=top_alternatives,
                is_target_best=evaluation_result["is_target_best"],
                best_profession=evaluation_result["best_profession"],
            )

            logger.info(
                f"Analysis completed. Target match: {target_result['match_percent']:.2f}%"
            )
            logger.info(f"Is target best: {evaluation_result['is_target_best']}")
            if not evaluation_result["is_target_best"]:
                logger.info(
                    f"Better profession found: {evaluation_result['best_profession']}"
                )

            return response

        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"Error evaluating resume: {str(e)}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, f"Evaluation error: {str(e)}")

        return ml_service_pb2.ResumeResponse()

    def _create_profession_match(
        self, prof_name: str, result: dict
    ) -> ml_service_pb2.ProfessionMatch:
        """Создает protobuf объект ProfessionMatch из dict результата"""
        pb_result = ml_service_pb2.ProfessionMatch(
            name=prof_name, match_percent=result["match_percent"]
        )

        # Добавляем missing_skills
        for skill in result.get("missing_skills", []):
            missing_skill = ml_service_pb2.MissingSkill(
                name=skill["name"],
                required_level=skill["required_level"],
                candidate_level=skill["candidate_level"],
            )
            pb_result.missing_skills.append(missing_skill)

        # Добавляем final_levels
        for comp_name, level in result.get("final_levels", {}).items():
            pb_result.final_levels[comp_name] = level

        return pb_result


async def main():
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ],
    )

    ml_service_pb2_grpc.add_ResumeAnalyzerServicer_to_server(
        ResumeAnalyzerServicer(), server
    )

    port = 50051
    server.add_insecure_port(f"[::]:{port}")

    logger.info(f"Starting gRPC server on port {port}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
