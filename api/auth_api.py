from constants import REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester

class AuthAPI(CustomRequester):
    """Класс для работы с аутентификацией."""

    def __init__(self, session):
        super().__init__(session=session, base_url="https://auth.dev-cinescope.f5qa.ru")  # без / в конце

    def register_user(self, user_data, expected_status=201):
        """Регистрация нового пользователя."""
        return self.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,  # REGISTER_ENDPOINT = "/register"
            data=user_data,
            expected_status=expected_status
        )

    def login_user(self, login_data, expected_status=201):
        """Авторизация пользователя."""
        return self.send_request(
            method="POST",
            endpoint=LOGIN_ENDPOINT,  # LOGIN_ENDPOINT = "/login"
            data=login_data,
            expected_status=expected_status
        )