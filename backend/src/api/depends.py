from resource.auth import oauth2_scheme
from typing import Annotated

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from core.config import settings
from core.exceptions import CredentialsException
from infrastructure.postgres.database import PostgresDatabase
from infrastructure.postgres.repository.competence_repo import (
    CompetenceRepository,
)
from infrastructure.postgres.repository.profession_repo import (
    ProfessionRepository,
)
from infrastructure.postgres.repository.user_repo import UserRepository
from schemas.auth import TokenData
from schemas.user import UserSchema

user_repo = UserRepository()
database = PostgresDatabase()
profession_repo = ProfessionRepository()
competence_repo = CompetenceRepository()

AUTH_EXCEPTION_MESSAGE = "Невозможно проверить данные для авторизации"


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_AUTH_KEY.get_secret_value(),
            algorithms=[settings.AUTH_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsException(detail=AUTH_EXCEPTION_MESSAGE)
        token_data = TokenData(username=username)
    except JWTError:
        raise CredentialsException(detail=AUTH_EXCEPTION_MESSAGE)

    async with database.session() as session:
        user = await user_repo.get_user_by_email(
            session=session,
            email=token_data.username,
        )

    if user is None:
        raise CredentialsException(detail=AUTH_EXCEPTION_MESSAGE)

    return user


def check_for_admin_access(user: UserSchema) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только админ имеет права добавлять/изменять/удалять данные.",
        )
