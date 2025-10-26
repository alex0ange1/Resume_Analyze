from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError

from project.schemas.competence import CompetenceSchema, CompetenceCreateUpdateSchema
from project.infrastructure.postgres.models import Competence

from project.core.exceptions import (
    CompetenceNotFound,
    CompetenceAlreadyExists,
)


class CompetenceRepository:
    _collection: Type[Competence] = Competence

    async def get_competence_by_id(
        self,
        session: AsyncSession,
        competence_id: int,
    ) -> CompetenceSchema:
        query = select(self._collection).where(self._collection.id == competence_id)

        competence = await session.scalar(query)

        if not competence:
            raise CompetenceNotFound(_id=competence_id)

        return CompetenceSchema.model_validate(obj=competence)

    async def get_all_competencies(
        self,
        session: AsyncSession,
    ) -> list[CompetenceSchema]:
        query = select(self._collection)

        competencies = await session.scalars(query)

        return [
            CompetenceSchema.model_validate(obj=competence)
            for competence in competencies.all()
        ]

    async def create_competence(
        self,
        session: AsyncSession,
        competence: CompetenceCreateUpdateSchema,
    ) -> CompetenceSchema:
        query = (
            insert(self._collection)
            .values(competence.model_dump())
            .returning(self._collection)
        )

        try:
            created_competence = await session.scalar(query)
            await session.flush()
        except IntegrityError:
            raise CompetenceAlreadyExists(name=competence.name)

        return CompetenceSchema.model_validate(obj=created_competence)

    async def update_competence(
        self,
        session: AsyncSession,
        competence_id: int,
        competence: CompetenceCreateUpdateSchema,
    ) -> CompetenceSchema:
        query = (
            update(self._collection)
            .where(self._collection.id == competence_id)
            .values(competence.model_dump())
            .returning(self._collection)
        )

        updated_competence = await session.scalar(query)

        if not updated_competence:
            raise CompetenceNotFound(_id=competence_id)

        return CompetenceSchema.model_validate(obj=updated_competence)

    async def delete_competence(
        self, session: AsyncSession, competence_id: int
    ) -> None:
        query = delete(self._collection).where(self._collection.id == competence_id)

        result = await session.execute(query)

        if not result.rowcount:
            raise CompetenceNotFound(_id=competence_id)
