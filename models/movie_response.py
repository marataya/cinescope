# models/movie_response.py
import datetime
from typing import Literal, Any

from pydantic import BaseModel, Field, ConfigDict, field_validator


class MovieResponse(BaseModel):
    model_config = ConfigDict(
        extra='allow',
        from_attributes=True,
        populate_by_name=True, # позволяет принимать и image_url и imageUrl
    )

    # PK serial4
    id: int

    # text not null
    name: str = Field(min_length=1)
    price: int = Field(ge=0) # int4 not null
    description: str # text not null по сигнатуре

    # text nullable
    image_url: str | None = Field(default=None, alias="imageUrl", validation_alias="imageUrl")

    # enum Location not null
    location: Literal["MSK", "SPB"]

    # bool not null default false
    published: bool = Field(default=False)

    # float8 not null default '0'
    rating: float = Field(default=0, ge=0, le=10)

    # int4 not null FK
    genre_id: int = Field(alias="genreId", validation_alias="genreId")

    # timestamp(3) not null default CURRENT_TIMESTAMP
    created_at: datetime.datetime | str | None = Field(
        default=None, alias="createdAt", validation_alias="createdAt"
    )

    # nested from API?join=...
    genre: dict | None = None
    reviews: list[Any] | None = None
    updatedAt: str | None = None

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_created_at(cls, value):
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value
        # API returns ISO string, DB returns datetime
        try:
            return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(f"Некорректный формат created_at: {value}, ожидается ISO 8601")

    @field_validator("image_url", mode="before")
    @classmethod
    def empty_to_none(cls, v):
        # бек иногда возвращает "" вместо null
        if v == "":
            return None
        return v