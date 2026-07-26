from api.auth_api import AuthApi
from api.genres_api import GenresApi
from api.movies_api import MoviesApi
from api.user_api import UserApi


class ApiManager:
    def __init__(self, session):
        self.session = session
        self.auth_api = AuthApi(session)
        self.movies_api = MoviesApi(session)
        self.genres_api = GenresApi(session)
        self.user_api = UserApi(session)

    # для совместимости со старыми тестами super_admin.api.create_user
    def create_user(self, payload, expected_status=201):
        return self.user_api.create_user(payload, expected_status=expected_status)

    def delete_user(self, user_id, expected_status=200):
        return self.user_api.delete_user(user_id, expected_status=expected_status)

    def close_session(self):
        self.session.close()