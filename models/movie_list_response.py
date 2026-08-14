# models/movies_list_response.py
from typing import List

from pydantic import BaseModel, ConfigDict

from models.movie_response import MovieResponse


class MoviesListResponse(BaseModel):
    model_config = ConfigDict(extra='allow', from_attributes=True, populate_by_name=True)

    movies: List[MovieResponse]
    count: int
    page: int
    pageSize: int = 10

    totalPages: int | None = None