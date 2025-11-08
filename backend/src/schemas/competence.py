from pydantic import BaseModel, ConfigDict, Field


class CompetenceCreateUpdateSchema(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Название компетенции",
        examples=["Python", "SQL", "Управление проектами"],
    )


class CompetenceSchema(CompetenceCreateUpdateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
