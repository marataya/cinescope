from typing import Annotated

from pydantic import BaseModel, Field, field_validator, EmailStr

from constants.roles import Roles
from utils.data_generator import DataGenerator


class TestUser(BaseModel):
    email: EmailStr
    fullName: Annotated[str, Field(min_length=2, max_length=100)]
    password: Annotated[str, Field(min_length=8, max_length=20)]
    passwordRepeat: Annotated[str, Field(min_length=8, max_length=20, description="Пароли должны совпадать")]
    roles: Annotated[list[Roles], Field(default_factory=lambda: [Roles.USER])]
    verified: bool | None = None
    banned: bool | None = None

    @field_validator("passwordRepeat")
    @classmethod
    def check_password_repeat(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    # валидация что пароли совпадают
    # def model_post_init(self, __context):
    #     if self.password!= self.passwordRepeat:
    #         raise ValueError("password!= passwordRepeat")


    @property
    def creds(self) -> dict:
        return {"email": self.email, "password": self.password}

    def to_api_dict(self) -> dict:
        # mode="json" превратит Roles enum в строку + EmailStr в строку
        data = self.model_dump(mode="json", exclude_none=True)
        # API ждет roles как строки ["USER"] а не [{"value":...}]
        if "roles" in data:
            data["roles"] = [r.value if isinstance(r, Roles) else r for r in self.roles]
        return data

    def to_db_dict(self) -> dict:
        """Для прямой вставки через DBHelper -> UserDBModel"""
        return {
            "id": DataGenerator.generate_uuid() if hasattr(self, 'id') else None, # если у тебя id генерит БД - убери
            "email": str(self.email),
            "full_name": self.fullName,
            "password": self.password, # тут должен быть хеш, если вставляешь напрямую
            "verified": self.verified if self.verified is not None else True,
            "banned": self.banned if self.banned is not None else False,
            "roles": [r.value for r in self.roles],
        }

    def model_dump_for_admin(self) -> dict:
        """Для POST /user через super_admin"""
        data = self.to_api_dict()
        data["verified"] = True if self.verified is None else self.verified
        data["banned"] = False if self.banned is None else self.banned
        return data