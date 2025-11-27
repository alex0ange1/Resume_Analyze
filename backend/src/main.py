import asyncio
import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.auth_routes import auth_router
from api.competence_routes import competence_router
from api.profession_routes import profession_router
from api.user_routes import user_router
from api.ml_routes import ml_router
from core.config import settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app_options = {}
    if settings.ENV.lower() == "prod":
        app_options = {
            "docs_url": None,
            "redoc_url": None,
        }
    if settings.LOG_LEVEL in ["DEBUG", "INFO"]:
        app_options["debug"] = True

    app = FastAPI(root_path=settings.ROOT_PATH, **app_options)
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=settings.ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(user_router, tags=["User"])
    app.include_router(auth_router, tags=["Auth"])

    app.include_router(profession_router, tags=["Profession"])
    app.include_router(competence_router, tags=["Competence"])

    app.include_router(ml_router, tags=["ML"])

    return app


app = create_app()


async def run() -> None:
    config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=False)
    server = uvicorn.Server(config=config)
    tasks = (asyncio.create_task(server.serve()),)

    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)


if __name__ == "__main__":
    logger.debug(f"{settings.postgres_url}=")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
