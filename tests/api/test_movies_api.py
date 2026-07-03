import pytest
from constants import Endpoints
from utils.data_generator import DataGenerator

class TestMoviesPublic:
    def test_get_movie_by_id(self, public_requester, created_movie):
        resp = public_requester.send_request(
            "GET",
            Endpoints.MOVIE_BY_ID.format(created_movie),
            expected_status=200
        )
        assert resp.json()["id"] == created_movie

    def test_get_movies_list_default(self, public_requester):
        resp = public_requester.send_request("GET", Endpoints.MOVIES, expected_status=200)
        data = resp.json()
        assert "movies" in data
        assert data["pageSize"] <= 20

    def test_get_movies_list_filters(self, public_requester, faker):
        params = {
            "pageSize": faker.random_int(min=1, max=20),
            "page": 1,
            "minPrice": 1,
            "maxPrice": 1000,
            "locations": ["MSK", "SPB"],
            "published": True
        }
        resp = public_requester.send_request("GET", Endpoints.MOVIES, params=params, expected_status=200)
        assert len(resp.json()["movies"]) <= params["pageSize"]

    def test_get_movie_not_found(self, public_requester):
        public_requester.send_request(
            "GET",
            Endpoints.MOVIE_BY_ID.format(999999),
            expected_status=404
        )

    def test_get_movies_invalid_page_size(self, public_requester):
        public_requester.send_request(
            "GET",
            Endpoints.MOVIES,
            params={"pageSize": 21},
            expected_status=400
        )

class TestMoviesSuperAdmin:
    def test_create_movie_success(self, api_requester, created_genre, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": faker.random_int(min=50, max=500),
            "description": faker.paragraph(nb_sentences=2),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        resp = api_requester.send_request("POST", Endpoints.MOVIES, data=payload, expected_status=201)
        movie_id = resp.json()["id"]
        api_requester.send_request("DELETE", Endpoints.MOVIE_BY_ID.format(movie_id), expected_status=200)

    def test_patch_movie(self, api_requester, created_movie, faker):
        payload = {"price": faker.random_int(min=100, max=999), "published": False}
        resp = api_requester.send_request(
            "PATCH",
            Endpoints.MOVIE_BY_ID.format(created_movie),
            data=payload,
            expected_status=200
        )
        assert resp.json()["price"] == payload["price"]

    def test_delete_movie(self, api_requester, public_requester, created_genre, faker):
        payload = {
            "name": "To Delete",
            "price": 100,
            "description": DataGenerator.generate_random_name(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        movie_id = api_requester.send_request("POST", Endpoints.MOVIES, data=payload, expected_status=201).json()["id"]
        api_requester.send_request("DELETE", Endpoints.MOVIE_BY_ID.format(movie_id), expected_status=200)
        public_requester.send_request("GET", Endpoints.MOVIE_BY_ID.format(movie_id), expected_status=404)

class TestMoviesValidation:
    def test_create_movie_missing_required_field(self, api_requester, created_genre):
        payload = {
            "price": 100,
            "description": "no name",
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": "https://test.com/img.jpg"
        }
        api_requester.send_request("POST", Endpoints.MOVIES, data=payload, expected_status=400)

    def test_create_movie_invalid_genre(self, api_requester, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": 999999,
            "imageUrl": faker.image_url()
        }
        api_requester.send_request("POST", Endpoints.MOVIES, data=payload, expected_status=400)

class TestMoviesAuth:
    def test_create_movie_without_token_unauthorized(self, public_requester, created_genre, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        public_requester.send_request("POST", Endpoints.MOVIES, data=payload, expected_status=401)

    def test_patch_movie_without_token_unauthorized(self, public_requester, created_movie):
        public_requester.send_request(
            "PATCH",
            Endpoints.MOVIE_BY_ID.format(created_movie),
            data={"price": 777},
            expected_status=401
        )

    def test_delete_movie_without_token_unauthorized(self, public_requester, created_movie):
        public_requester.send_request(
            "DELETE",
            Endpoints.MOVIE_BY_ID.format(created_movie),
            expected_status=401
        )