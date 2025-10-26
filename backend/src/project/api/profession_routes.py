from fastapi import APIRouter, Depends, HTTPException, status

from project.api.depends import (
    check_for_admin_access,
    database,
    get_current_user,
    profession_repo,
)
from project.core.exceptions import (
    ProfessionAlreadyExists,
    ProfessionNotFound,
    CompetenceNotFound,
    InvalidCompetencyLevel,
)
from project.schemas.profession import ProfessionCreateUpdateSchema, ProfessionSchema
from project.schemas.user import UserSchema


profession_router = APIRouter()


@profession_router.get(
    "/all_professions",
    response_model=list[ProfessionSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_all_professions() -> list[ProfessionSchema]:
    async with database.session() as session:
        all_professions = await profession_repo.get_all_professions(session=session)

    return all_professions


@profession_router.get(
    "/profession/{profession_id}",
    response_model=ProfessionSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_profession_by_id(
    profession_id: int,
) -> ProfessionSchema:
    try:
        async with database.session() as session:
            profession = await profession_repo.get_profession_by_id(
                session=session, profession_id=profession_id
            )
    except ProfessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)

    return profession


@profession_router.post(
    "/add_profession",
    response_model=ProfessionSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_profession(
    profession_dto: ProfessionCreateUpdateSchema,
    current_user: UserSchema = Depends(get_current_user),
) -> ProfessionSchema:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            new_profession = await profession_repo.create_profession(
                session=session, profession=profession_dto
            )
    except ProfessionAlreadyExists as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.message)
    except CompetenceNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except InvalidCompetencyLevel as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error.message
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return new_profession


@profession_router.put(
    "/update_profession/{profession_id}",
    response_model=ProfessionSchema,
    status_code=status.HTTP_200_OK,
)
async def update_profession(
    profession_id: int,
    profession_dto: ProfessionCreateUpdateSchema,
    current_user: UserSchema = Depends(get_current_user),
) -> ProfessionSchema:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            updated_profession = await profession_repo.update_profession(
                session=session,
                profession_id=profession_id,
                profession=profession_dto,
            )
    except ProfessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except CompetenceNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except InvalidCompetencyLevel as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error.message
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return updated_profession


@profession_router.delete(
    "/delete_profession/{profession_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profession(
    profession_id: int,
    current_user: UserSchema = Depends(get_current_user),
) -> None:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            await profession_repo.delete_profession(
                session=session, profession_id=profession_id
            )
    except ProfessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
