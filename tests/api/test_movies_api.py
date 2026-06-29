import requests

from constants import HEADERS, Endpoints


class TestMoviesPublic:
    """GET методы - публичные, работают без токена"""

    def test_get_movie_by_id(self, api_base_url, created_movie):
        resp = requests.get(f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(created_movie)}", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == created_movie
        assert "rating" in data
        assert 0 <= data["rating"] <= 5
        assert "reviews" in data
        assert isinstance(data["reviews"], list)

    def test_get_movies_list_default(self, api_base_url):
        resp = requests.get(f"{api_base_url}{Endpoints.MOVIES}", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "movies" in data
        assert "page" in data
        assert "pageSize" in data
        assert data["page"] == 1
        assert data["pageSize"] <= 20

    def test_get_movies_list_filters(self, api_base_url, faker):
        params = {
            "pageSize": faker.random_int(min=1, max=20),
            "page": 1,
            "minPrice": 1,
            "maxPrice": 1000,
            "locations": ["MSK", "SPB"],
            "published": True
        }
        resp = requests.get(f"{api_base_url}{Endpoints.MOVIES}", params=params, headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["movies"]) <= params["pageSize"]
        if data["movies"]:
            assert data["movies"][0]["published"] is True

    def test_get_movie_not_found(self, api_base_url):
        resp = requests.get(f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(999999)}", headers=HEADERS)
        assert resp.status_code == 404

    def test_get_movies_invalid_page_size(self, api_base_url):
        params = {"pageSize": 21}  # максимум 20
        resp = requests.get(f"{api_base_url}{Endpoints.MOVIES}", params=params, headers=HEADERS)
        assert resp.status_code in (400, 422)


class TestMoviesSuperAdmin:
    """POST/PATCH/DELETE - только SUPER_ADMIN"""

    def test_create_movie_success(self, api_session, api_base_url, created_genre, faker):
        payload = {
            "name": faker.catch_phrase(),
            "price": faker.random_int(min=50, max=500),
            "description": faker.paragraph(nb_sentences=2),
            "location": faker.random_element(["MSK", "SPB"]),
            "published": faker.boolean(),
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        resp = api_session.post(f"{api_base_url}{Endpoints.MOVIES}", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == payload["name"]
        assert data["price"] == payload["price"]
        assert "id" in data

        # cleanup
        api_session.delete(f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(data['id'])}")

    def test_patch_movie(self, api_session, api_base_url, created_movie, faker):
        payload = {
            "name": faker.bs().capitalize(),
            "price": faker.random_int(min=100, max=999),
            "published": False
        }
        resp = api_session.patch(
            f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(created_movie)}",
            json=payload
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["price"] == payload["price"]
        assert data["published"] is False

    def test_delete_movie(self, api_session, api_base_url, created_genre, faker):
        # создаем фильм специально для удаления
        payload = {
            "name": "To Delete",
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        movie_id = api_session.post(f"{api_base_url}{Endpoints.MOVIES}", json=payload).json()["id"]

        resp = api_session.delete(f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(movie_id)}")
        assert resp.status_code == 200
        assert resp.json()["id"] == movie_id

        # проверяем что реально удалился
        get_resp = requests.get(f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(movie_id)}", headers=HEADERS)
        assert get_resp.status_code == 404


class TestMoviesValidation:
    """Валидация данных - 400/422 ошибки"""

    def test_create_movie_missing_required_field(self, api_session, api_base_url, created_genre):
        payload = {
            "price": 100,
            "description": "no name",
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": "https://test.com/img.jpg"
        }
        resp = api_session.post(f"{api_base_url}{Endpoints.MOVIES}", json=payload)
        assert resp.status_code in (400, 422)

    def test_create_movie_invalid_genre(self, api_session, api_base_url, faker):
        payload = {
            "name": faker.word(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": "invalid-uuid",
            "imageUrl": faker.image_url()
        }
        resp = api_session.post(f"{api_base_url}{Endpoints.MOVIES}", json=payload)
        assert resp.status_code in (400, 404, 422)


class TestMoviesAuth:
    """Проверки авторизации"""

    def test_create_movie_without_token_unauthorized(self, api_base_url, created_genre, faker):
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

    def test_patch_movie_without_token_unauthorized(self, api_base_url, created_movie):
        resp = requests.patch(
            f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(created_movie)}",
            json={"price": 777},
            headers=HEADERS
        )
        assert resp.status_code == 401

    def test_delete_movie_without_token_unauthorized(self, api_base_url, created_movie):
        resp = requests.delete(
            f"{api_base_url}{Endpoints.MOVIE_BY_ID.format(created_movie)}",
            headers=HEADERS
        )
        assert resp.status_code == 401