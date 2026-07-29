from typing import Optional

from pydantic import BaseModel, Field, field_validator, EmailStr

from constants.roles import Roles


class TestUser(BaseModel):
    email: EmailStr
    fullName: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=20)
    passwordRepeat: str = Field(min_length=8, max_length=20, description="Пароли должны совпадать")
    roles: list[Roles] = Field(default_factory=lambda: [Roles.USER])
    verified: Optional[bool] = None
    banned: Optional[bool] = None

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

    # @classmethod
    # def random(cls) -> "TestUser":
    #     pwd = DataGenerator.generate_random_password()
    #     return cls(
    #         email=DataGenerator.generate_random_email(),
    #         fullName=DataGenerator.generate_random_name(),
    #         password=pwd,
    #         passwordRepeat=pwd,
    #         roles=[Roles.USER.value]
    #     )

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

    def model_dump_for_admin(self) -> dict:
        """Для POST /user через super_admin"""
        data = self.to_api_dict()
        data["verified"] = True if self.verified is None else self.verified
        data["banned"] = False if self.banned is None else self.banned
        return data