import allure
import pytest

from utils.data_generator import DataGenerator


@allure.epic("Test User Roles")
class TestUserRoles:

    @allure.title("Создание пользователя через SUPER_ADMIN - проверка полей")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_user(self, super_admin, creation_user_data):
        response = super_admin.api.user_api.create_user(creation_user_data)

        assert response.get('id') and response['id'] != '', "ID должен быть не пустым"
        assert response.get('email') == creation_user_data['email']
        assert response.get('fullName') == creation_user_data['fullName']
        assert response.get('roles', []) == creation_user_data['roles']
        assert response.get('verified') is True

    @allure.title("SUPER_ADMIN создает и удаляет пользователя")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_super_admin(self, super_admin):
        payload = DataGenerator.generate_user_payload(is_admin_create=True)
        user_resp = super_admin.api.user_api.create_user(payload)
        # достаем id
        user_id = user_resp.get("id") or user_resp.get("user", {}).get("id") or user_resp.get("_id")
        print(f"Created user: {user_resp}")
        super_admin.api.user_api.delete_user(user_id)

    @allure.title("Получение пользователя по ID и по email - ответы идентичны")
    @pytest.mark.regression
    def test_get_user_by_locator(self, super_admin, creation_user_data):
        created_user_response = super_admin.api.user_api.create_user(creation_user_data)
        response_by_id = super_admin.api.user_api.get_user(created_user_response['id'])
        response_by_email = super_admin.api.user_api.get_user(creation_user_data['email'])

        assert response_by_id == response_by_email, "Содержание ответов должно быть идентичным"
        assert response_by_id.get('id') and response_by_id['id'] != '', "ID должен быть не пустым"
        assert response_by_id.get('email') == creation_user_data['email']
        assert response_by_id.get('fullName') == creation_user_data['fullName']
        assert response_by_id.get('roles', []) == creation_user_data['roles']
        assert response_by_id.get('verified') is True

    @allure.title("USER не может получать других пользователей - 403")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)

