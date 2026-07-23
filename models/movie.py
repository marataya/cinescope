# models/movie.py
from pydantic import BaseModel
from datetime import datetime

from utils.data_generator import DataGenerator


class MovieResponse(BaseModel):
    id: int
    name: str
    price: int
    description: str
    imageUrl: str
    location: str
    published: bool
    rating: int
    genreId: int
    createdAt: datetime
    genre: dict
