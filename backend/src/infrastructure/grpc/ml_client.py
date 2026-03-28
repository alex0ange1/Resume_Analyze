import logging
import grpc
from typing import Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from proto import ml_service_pb2, ml_service_pb2_grpc

logger = logging.getLogger(__name__)


class MLServiceClient:
    def __init__(self, host: str = "ml_service", port: int = 50051):
        self.host = host
        self.port = port
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub: Optional[ml_service_pb2_grpc.ResumeAnalyzerStub] = None

    async def connect(self):
        if not self.channel:
            self.channel = grpc.aio.insecure_channel(f"{self.host}:{self.port}")
            self.stub = ml_service_pb2_grpc.ResumeAnalyzerStub(self.channel)
            logger.info(f"Connected to ML service at {self.host}:{self.port}")

    async def close(self):
        if self.channel:
            await self.channel.close()
            logger.info("Closed connection to ML service")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def evaluate_resume(
        self,
        resume_text: str,
        target_profession: ml_service_pb2.Profession,
        all_professions: List[ml_service_pb2.Profession],
    ) -> ml_service_pb2.ResumeResponse:
        """
        Отправляет запрос в ML сервис для анализа резюме по всем профессиям

        Args:
            resume_text: текст резюме
            target_profession: целевая профессия в protobuf формате
            all_professions: список всех профессий в protobuf формате

        Returns:
            ResumeResponse от ML сервиса
        """
        if not self.stub:
            await self.connect()

        request = ml_service_pb2.ResumeRequest(
            resume_text=resume_text,
            target_profession=target_profession,
            all_professions=all_professions,
        )

        try:
            response = await self.stub.EvaluateResume(request)
            logger.info(
                f"Successfully evaluated resume. "
                f"Target: {response.target_result.name} ({response.target_result.match_percent:.1f}%), "
                f"Is best: {response.is_target_best}"
            )
            return response
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            logger.error(f"Error calling ML service: {str(e)}")
            raise
