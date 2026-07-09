import allure
import pytest

from utils.data_generator import DataGenerator


@allure.epic("Auth API")
class TestAuthRegister:
    @allure.title("Успешная регистрация пользователя")
    def test_register_success(self, api_manager):
        payload = DataGenerator.generate_user_payload()
        resp = api_manager.auth_api.register_user(user_data=payload, expected_status=201)
        data = resp.json()
        assert data["email"] == payload["email"]
        assert data["fullName"] == payload["fullName"]
        assert "id" in data
        assert "password" not in data
        assert data["verified"] is True # бэк сразу верифицирует
        assert "USER" in data["roles"]

    @allure.title("Регистрация с существующим email")
    def test_register_duplicate_email_conflict(self, api_manager, registered_user):
        payload = DataGenerator.generate_user_payload()
        payload["email"] = registered_user["email"]

        api_manager.auth_api.register_user(user_data=payload, expected_status=409)

    @allure.title("Регистрация с невалидным email")
    @pytest.mark.parametrize("email", ["invalid", "test@", "@test.com", "test.com"])
    def test_register_invalid_email(self, api_manager, email):
        payload = DataGenerator.generate_user_payload()
        payload["email"] = email

        api_manager.auth_api.register_user(user_data=payload, expected_status=400)

    @allure.title("Регистрация с коротким паролем")
    def test_register_short_password(self, api_manager):
        payload = DataGenerator.generate_user_payload()
        payload["password"] = "123"
        payload["passwordRepeat"] = "123"

        api_manager.auth_api.register_user(user_data=payload, expected_status=400)

    @allure.title("Регистрация с несовпадающими паролями")
    def test_register_password_mismatch(self, api_manager):
        payload = DataGenerator.generate_user_payload()
        payload["passwordRepeat"] = payload["password"] + "123"

        api_manager.auth_api.register_user(user_data=payload, expected_status=400)

    @allure.title("Регистрация без обязательных полей")
    @pytest.mark.parametrize("field", ["email", "password", "passwordRepeat", "fullName"])
    def test_register_missing_required_field(self, api_manager, field):
        payload = DataGenerator.generate_user_payload()
        del payload[field]

        api_manager.auth_api.register_user(user_data=payload, expected_status=400)

@allure.epic("Auth API")
class TestAuthLogin:
    @allure.title("Успешный логин")
    def test_login_success(self, api_manager, registered_user):
        resp = api_manager.auth_api.login_user(
            credentials={
                "email": registered_user["email"],
                "password": registered_user["password"]
            },
            expected_status=201
        )
        data = resp.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["user"]["email"] == registered_user["email"]

    @allure.title("Логин с неверным паролем")
    def test_login_wrong_password(self, api_manager, registered_user):
        api_manager.auth_api.login_user(
            credentials={
                "email": registered_user["email"],
                "password": "wrong_password123"
            },
            expected_status=401
        )

    @allure.title("Логин несуществующего пользователя")
    def test_login_user_not_found(self, api_manager):
        api_manager.auth_api.login_user(
            credentials={
                "email": "notexist@test.com",
                "password": "password123"
            },
            expected_status=401
        )

    @allure.title("Логин с невалидным email")
    def test_login_invalid_email_format(self, api_manager):
        api_manager.auth_api.login_user(
            credentials={
                "email": "invalid_email",
                "password": "password123"
            },
            expected_status=401
        )

@allure.epic("Auth API")
class TestAuthRefresh:
    @allure.title("Обновление токена без куки")
    def test_refresh_token_unauthorized(self, api_manager):
        # По логу бэк возвращает 401 без куки refresh_token
        api_manager.auth_api.send_request(
            "GET",
            "/refresh-tokens",
            expected_status=401
        )