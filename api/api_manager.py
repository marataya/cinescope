from api.auth_api import AuthApi
from api.movies_api import MoviesApi
from api.genres_api import GenresApi

class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthApi(session)
        self.movies_api = MoviesApi(session)
        self.genres_api = GenresApi(session)