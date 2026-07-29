import datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, EmailStr
from constants.roles import Roles


class RegisterUserResponse(BaseModel):
    id: str
    email: Annotated[EmailStr, Field(description="Email пользователя")]
    fullName: Annotated[str, Field(min_length=1, max_length=100, description="Полное имя пользователя")]
    verified: bool
    banned: bool
    roles: list[Roles]
    createdAt: Annotated[str, Field(description="Дата и время создания пользователя в формате ISO 8601")]

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value