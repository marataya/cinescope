import pytest
from utils.data_generator import DataGenerator


class TestAuth:
    def test_login_returns_all_tokens(self, api_manager, valid_credentials):
        resp = api_manager.auth_api.login_user(valid_credentials, expected_status=201)
        data = resp.json()
        assert "accessToken" in data
        assert "user" in data
        assert data["user"]["email"] == valid_credentials["email"]

    def test_access_api_with_valid_token(self, api_requester):
        resp = api_requester.send_request("GET", "/movies", expected_status=200)
        assert "movies" in resp.json()

    def test_access_api_without_token_public(self, public_requester):
        resp = public_requester.send_request("GET", "/movies", expected_status=200)
        assert "movies" in resp.json()

    def test_register_user(self, api_manager, faker):
        user_data = {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_random_name(),
            "password": DataGenerator.generate_random_password(),
            "passwordRepeat": None,
            "roles": ["USER"]
        }
        user_data["passwordRepeat"] = user_data["password"]

        resp = api_manager.auth_api.register_user(user_data, expected_status=201)
        data = resp.json()
        assert data["email"] == user_data["email"]
        assert data["fullName"] == user_data["fullName"]

    def test_super_admin_can_create_movie(self, api_requester, created_genre, faker):
        payload = {
            "name": faker.catch_phrase(),
            "price": faker.random_int(min=50, max=500),
            "description": faker.paragraph(nb_sentences=2),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        resp = api_requester.send_request("POST", "/movies", data=payload, expected_status=201)
        movie_id = resp.json()["id"]
        api_requester.send_request("DELETE", f"/movies/{movie_id}", expected_status=200)

    def test_create_movie_without_token_forbidden(self, public_requester, created_genre, faker):
        payload = {
            "name": faker.word(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        public_requester.send_request("POST", "/movies", data=payload, expected_status=401)