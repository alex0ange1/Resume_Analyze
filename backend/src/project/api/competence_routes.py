from fastapi import APIRouter, Depends, HTTPException, status

from project.api.depends import (
    check_for_admin_access,
    database,
    get_current_user,
    competence_repo,
)
from project.core.exceptions import (
    CompetenceAlreadyExists,
    CompetenceNotFound,
)
from project.schemas.competence import CompetenceCreateUpdateSchema, CompetenceSchema
from project.schemas.user import UserSchema


competence_router = APIRouter()


@competence_router.get(
    "/all_competencies",
    response_model=list[CompetenceSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_all_competencies() -> list[CompetenceSchema]:
    async with database.session() as session:
        all_competencies = await competence_repo.get_all_competencies(session=session)

    return all_competencies


@competence_router.get(
    "/competence/{competence_id}",
    response_model=CompetenceSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_competence_by_id(
    competence_id: int,
) -> CompetenceSchema:
    try:
        async with database.session() as session:
            competence = await competence_repo.get_competence_by_id(
                session=session, competence_id=competence_id
            )
    except CompetenceNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)

    return competence


@competence_router.post(
    "/add_competence",
    response_model=CompetenceSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_competence(
    competence_dto: CompetenceCreateUpdateSchema,
    current_user: UserSchema = Depends(get_current_user),
) -> CompetenceSchema:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            new_competence = await competence_repo.create_competence(
                session=session, competence=competence_dto
            )
    except CompetenceAlreadyExists as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.message)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return new_competence


@competence_router.put(
    "/update_competence/{competence_id}",
    response_model=CompetenceSchema,
    status_code=status.HTTP_200_OK,
)
async def update_competence(
    competence_id: int,
    competence_dto: CompetenceCreateUpdateSchema,
    current_user: UserSchema = Depends(get_current_user),
) -> CompetenceSchema:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            updated_competence = await competence_repo.update_competence(
                session=session,
                competence_id=competence_id,
                competence=competence_dto,
            )
    except CompetenceNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return updated_competence


@competence_router.delete(
    "/delete_competence/{competence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_competence(
    competence_id: int,
    current_user: UserSchema = Depends(get_current_user),
) -> None:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            await competence_repo.delete_competence(
                session=session, competence_id=competence_id
            )
    except CompetenceNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
