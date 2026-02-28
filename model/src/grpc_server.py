import asyncio
import logging
import grpc
from concurrent import futures


from proto import ml_service_pb2, ml_service_pb2_grpc

logger = logging.getLogger(__name__)


class ResumeAnalyzerServicer(ml_service_pb2_grpc.ResumeAnalyzerServicer):
    async def EvaluateResume(
        self, request: ml_service_pb2.ResumeRequest, context: grpc.aio.ServicerContext
    ) -> ml_service_pb2.ResumeResponse:
        try:
            logger.info(f"Evaluating resume for profession: {request.profession}")

            result = {
                "final_levels": {
                    "Определения, история развития и главные тренды ИИ": 2,
                    "Процесс, стадии и методологии разработки решений на основе ИИ (Docker, Linux/Bash, Git)": 2,
                    "Статистические методы и первичный анализ данных": 3,
                    "Оценка качества работы методов ИИ": 2,
                    "Языки программирования и библиотеки (Python, C++)": 3,
                    "SQL базы данных (GreenPLum, Postgres, Oracle)": 2,
                    "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, Neo4J, Hbase)": 1,
                    "Hadoop, SPARK, Hive": 1,
                    "Качество и предобработка данных, подходы и инструменты": 3,
                    "Работа с распределенной кластерной системой": 1,
                    "Методы машинного обучения": 3,
                    "Рекомендательные системы": 2,
                    "Методы оптимизации": 2,
                    "Основы глубокого обучения": 3,
                    "Анализ изображений и видео": 1,
                    "Машинное обучение на больших данных": 2,
                    "Глубокое обучение для анализа естественного языка": 3,
                    "Обучение с подкреплением и глубокое обучение с подкреплением": 1,
                    "Глубокое обучение для анализа и генерации изображений, видео": 1,
                    "Анализ естественного языка": 3,
                    "Информационный поиск": 2,
                    "Массово параллельные вычисления для ускорения машинного обучения (GPU)": 2,
                    "Потоковая обработка данных (data streaming, event processing)": 1,
                    "Массово параллельная обработка и анализ данных": 2,
                },
                "evaluation": {
                    "match_percent": 56.5,
                    "missing_skills": [
                        {
                            "name": "NoSQL базы данных (Cassandra, MongoDB, ElasticSearch, Neo4J, Hbase)",
                            "required_level": 2,
                            "candidate_level": 1,
                        },
                        {
                            "name": "Hadoop, SPARK, Hive",
                            "required_level": 2,
                            "candidate_level": 1,
                        },
                        {
                            "name": "Работа с распределенной кластерной системой",
                            "required_level": 2,
                            "candidate_level": 1,
                        },
                    ],
                },
            }

            final_levels = {}
            for comp, level in result["final_levels"].items():
                final_levels[comp] = level

            missing_skills = []
            for skill in result["evaluation"]["missing_skills"]:
                missing_skills.append(
                    ml_service_pb2.MissingSkill(
                        name=skill["name"],
                        required_level=skill["required_level"],
                        candidate_level=skill["candidate_level"],
                    )
                )

            response = ml_service_pb2.ResumeResponse(
                final_levels=final_levels,
                evaluation=ml_service_pb2.Evaluation(
                    match_percent=result["evaluation"]["match_percent"],
                    missing_skills=missing_skills,
                ),
            )

            logger.info(
                f"Successfully evaluated resume. Match: {result['evaluation']['match_percent']:.2f}%"
            )
            return response

        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            logger.error(f"Error evaluating resume: {str(e)}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Evaluation error: {str(e)}")

        # Fallback (never reached, but needed for type checker)
        return ml_service_pb2.ResumeResponse()


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
