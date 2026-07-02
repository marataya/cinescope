import pytest
from constants import Endpoints

class TestAuth:
    def test_login_returns_all_tokens(self, auth_data):
        assert "accessToken" in auth_data
        assert "user" in auth_data
        assert auth_data["user"]["email"] == "api1@gmail.com"

    def test_access_api_with_valid_token(self, api_requester):
        # Проверка что токен рабочий - любой авторизованный запрос
        resp = api_requester.send_request("GET", Endpoints.MOVIES, expected_status=200)
        assert "movies" in resp.json()

    def test_access_api_without_token_public(self, public_requester):
        resp = public_requester.send_request("GET", Endpoints.MOVIES, expected_status=200)
        assert "movies" in resp.json()

    def test_super_admin_can_create_movie(self, api_requester, created_genre, faker):
        payload = {
            "name": faker.catch_phrase(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        resp = api_requester.send_request("POST", Endpoints.MOVIES, data=payload, expected_status=201)
        assert "id" in resp.json()
        api_requester.send_request("DELETE", Endpoints.MOVIE_BY_ID.format(resp.json()["id"]), expected_status=200)

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
        public_requester.send_request("POST", Endpoints.MOVIES, data=payload, expected_status=401)