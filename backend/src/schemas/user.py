from pydantic import BaseModel, ConfigDict, Field


class UserCreateUpdateSchema(BaseModel):
    email: str = Field(pattern=r"^\S+@\S+\.\S+$", examples=["email@mail.ru"])
    password: str
    is_admin: bool = False


class UserSchema(UserCreateUpdateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserRegisterCreateUpdateSchema(BaseModel):
    email: str = Field(pattern=r"^\S+@\S+\.\S+$", examples=["email@mail.ru"])
    password: str


class UserRegisterSchema(UserRegisterCreateUpdateSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
