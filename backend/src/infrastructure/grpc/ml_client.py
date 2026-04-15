import logging
import grpc
from typing import Optional
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
        self, resume_text: str, profession: str
    ) -> ml_service_pb2.ResumeResponse:
        if not self.stub:
            await self.connect()

        request = ml_service_pb2.ResumeRequest(
            resume_text=resume_text, profession=profession
        )

        try:
            response = await self.stub.EvaluateResume(request)
            logger.info(f"Successfully evaluated resume for profession: {profession}")
            return response
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e.code()} - {e.details()}")
            raise
        except Exception as e:
            logger.error(f"Error calling ML service: {str(e)}")
            raise
