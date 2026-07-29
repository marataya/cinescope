import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict


class RegisterUserResponse(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: str
    email: str
    fullName: str
    verified: bool
    roles: list[str]

    # optional
    banned: bool | None = None
    createdAt: str | None = None
    updatedAt: str | None = None

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        # Валидатор для проверки формата даты и времени (ISO 8601).
        try:
            datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value