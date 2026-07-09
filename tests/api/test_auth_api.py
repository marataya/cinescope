import pytest
from utils.data_generator import DataGenerator

class TestAuth:
    def test_login_returns_all_tokens(self, api_manager, valid_credentials):
        resp = api_manager.auth_api.login_user(valid_credentials, expected_status=201)
        data = resp.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert "user" in data

    def test_access_api_with_valid_token(self, authorized_api_manager, created_movie):
        resp = authorized_api_manager.movies_api.get_movie(created_movie)
        assert resp.status_code == 200

    def test_access_api_without_token_public(self, api_manager, created_movie):
        resp = api_manager.movies_api.get_movie(created_movie)
        assert resp.status_code == 200

    def test_register_user(self, api_manager, faker):
        password = DataGenerator.generate_random_password()
        payload = {
            "email": DataGenerator.generate_random_email(),  # 100% уникальный
            "fullName": DataGenerator.generate_random_name(),
            "password": password,
            "passwordRepeat": password,
            "roles": ["USER"]
        }
        resp = api_manager.auth_api.register_user(payload, expected_status=201)
        assert resp.json()["email"] == payload["email"]

    def test_super_admin_can_create_movie(self, authorized_api_manager, created_genre, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),  # с timestamp
            "price": faker.random_int(min=50, max=500),
            "description": faker.paragraph(nb_sentences=2),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        resp = authorized_api_manager.movies_api.create_movie(payload)
        movie_id = resp.json()["id"]
        authorized_api_manager.movies_api.delete_movie(movie_id)

    def test_create_movie_without_token_forbidden(self, api_manager, created_genre, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": 100,
            "description": "test",
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": "https://test.com/img.jpg"
        }
        api_manager.movies_api.create_movie(payload, expected_status=401)