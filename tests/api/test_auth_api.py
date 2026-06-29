import requests

from constants import HEADERS, Endpoints


class TestAuth:
    def test_login_returns_all_tokens(self, auth_data):
        """POST /login возвращает 201 и все токены"""
        assert "accessToken" in auth_data
        assert "refreshToken" in auth_data
        assert "expiresIn" in auth_data
        assert "user" in auth_data
        assert "SUPER_ADMIN" in auth_data["user"]["roles"]

    def test_access_api_with_valid_token(self, api_base_url, auth_headers):
        """Токен с f5qa.ru работает на coconutqa.ru"""
        resp = requests.get(f"{api_base_url}{Endpoints.MOVIES}", headers=auth_headers)
        assert resp.status_code == 200

    def test_access_api_without_token_public(self, api_base_url):
        """GET /movies публичный, должен отдавать 200 без токена"""
        resp = requests.get(f"{api_base_url}{Endpoints.MOVIES}", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "movies" in data

    def test_super_admin_can_create_movie(self, api_session, api_base_url, created_genre, faker):
        """POST /movies требует SUPER_ADMIN"""
        payload = {
            "name": faker.catch_phrase(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        resp = api_session.post(f"{api_base_url}{Endpoints.MOVIES}", json=payload)
        assert resp.status_code == 201

        # cleanup
        api_session.delete(f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(resp.json()['id'])}")

    def test_create_movie_without_token_forbidden(self, api_base_url, created_genre, faker):
        """POST /movies без токена должен быть 401"""
        payload = {
            "name": faker.word(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        resp = requests.post(f"{api_base_url}{Endpoints.MOVIES}", json=payload, headers=HEADERS)
        assert resp.status_code == 401