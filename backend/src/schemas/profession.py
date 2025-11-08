from typing import Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator

from core.exceptions import InvalidCompetencyLevel


class ProfessionCreateUpdateSchema(BaseModel):
    name: str
    competencies: Dict[int, int] = Field(
        default_factory=dict,
        description="Словарь где ключи - ID компетенций, значения - уровень владения (1-3)",
        examples=[{1: 2, 2: 3, 3: 1}],
    )

    @field_validator("competencies")
    @classmethod
    def validate_competency_levels(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Competencies must be a dictionary")

        for competence_id, level in v.items():
            if not isinstance(competence_id, int) or competence_id <= 0:
                raise ValueError("Competence IDs must be positive integers")
            if level not in (1, 2, 3):
                raise InvalidCompetencyLevel(level=level)

        return v


class ProfessionSchema(ProfessionCreateUpdateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
