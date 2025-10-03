from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, HTTPException, status, Depends
from jose import jwt

from project.core.config import settings
from project.core.exceptions import UserNotFound
from project.schemas.auth import Token
from project.api.depends import database, user_repo
from project.resource.auth import verify_password, get_password_hash
from project.schemas.user import UserCreateUpdateSchema
# from project.schemas.userregister import UserRegisterCreateUpdateSchema

auth_router = APIRouter()


@auth_router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        async with database.session() as session:
            user = await user_repo.get_user_by_email(session=session, email=form_data.username)

        if not verify_password(plain_password=form_data.password, hashed_password=user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except UserNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": user.email}

    to_encode = token_data.copy()
    if access_token_expires:
        expire = datetime.now(timezone.utc) + access_token_expires
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    access_token = jwt.encode(
        claims=to_encode,
        key=settings.SECRET_AUTH_KEY.get_secret_value(),
        algorithm=settings.AUTH_ALGORITHM,
    )

    return Token(access_token=access_token, token_type="bearer")


# @auth_router.post("/register", status_code=status.HTTP_201_CREATED)
# async def register_user(user_dto: UserRegisterCreateUpdateSchema) -> None:
#     try:
#         async with database.session() as session:
#             user = UserCreateUpdateSchema(login=user_dto.login,
#                                           email=user_dto.email,
#                                           password=get_password_hash(password=user_dto.password))
#             await user_repo.create_user(session=session, user=user)
#     except BaseException as error:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.args)
