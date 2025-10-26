from typing import Type, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError

from project.schemas.profession import ProfessionSchema, ProfessionCreateUpdateSchema
from project.infrastructure.postgres.models import Profession, Competence

from project.core.exceptions import (
    ProfessionNotFound,
    ProfessionAlreadyExists,
    CompetenceNotFound,
    InvalidCompetencyLevel,
)


class ProfessionRepository:
    _collection: Type[Profession] = Profession

    async def _validate_competencies_exist(
        self, session: AsyncSession, competencies: Dict[int, int]
    ) -> None:
        """Проверяет, что все competency_id существуют в базе"""
        if not competencies:
            return

        competence_ids = list(competencies.keys())
        query = select(Competence.id).where(Competence.id.in_(competence_ids))
        existing_ids = set(await session.scalars(query))

        missing_ids = set(competence_ids) - existing_ids
        if missing_ids:
            raise CompetenceNotFound(_id=list(missing_ids)[0])

    async def _validate_competency_levels(self, competencies: Dict[int, int]) -> None:
        """Проверяет, что уровни компетенций корректны"""
        for _, level in competencies.items():
            if level not in (1, 2, 3):
                raise InvalidCompetencyLevel(level=level)

    async def get_profession_by_id(
        self,
        session: AsyncSession,
        profession_id: int,
    ) -> ProfessionSchema:
        query = select(self._collection).where(self._collection.id == profession_id)

        profession = await session.scalar(query)

        if not profession:
            raise ProfessionNotFound(_id=profession_id)

        return ProfessionSchema.model_validate(obj=profession)

    async def get_all_professions(
        self,
        session: AsyncSession,
    ) -> list[ProfessionSchema]:
        query = select(self._collection)

        professions = await session.scalars(query)

        return [
            ProfessionSchema.model_validate(obj=profession)
            for profession in professions.all()
        ]

    async def create_profession(
        self,
        session: AsyncSession,
        profession: ProfessionCreateUpdateSchema,
    ) -> ProfessionSchema:
        query = (
            insert(self._collection)
            .values(profession.model_dump())
            .returning(self._collection)
        )

        await self._validate_competency_levels(profession.competencies)
        await self._validate_competencies_exist(session, profession.competencies)

        try:
            created_profession = await session.scalar(query)
            await session.flush()
        except IntegrityError:
            raise ProfessionAlreadyExists(name=profession.name)

        return ProfessionSchema.model_validate(obj=created_profession)

    async def update_profession(
        self,
        session: AsyncSession,
        profession_id: int,
        profession: ProfessionCreateUpdateSchema,
    ) -> ProfessionSchema:
        query = (
            update(self._collection)
            .where(self._collection.id == profession_id)
            .values(profession.model_dump())
            .returning(self._collection)
        )

        await self._validate_competency_levels(profession.competencies)
        await self._validate_competencies_exist(session, profession.competencies)

        updated_profession = await session.scalar(query)

        if not updated_profession:
            raise ProfessionNotFound(_id=profession_id)

        return ProfessionSchema.model_validate(obj=updated_profession)

    async def delete_profession(
        self, session: AsyncSession, profession_id: int
    ) -> None:
        query = delete(self._collection).where(self._collection.id == profession_id)

        result = await session.execute(query)

        if not result.rowcount:
            raise ProfessionNotFound(_id=profession_id)
