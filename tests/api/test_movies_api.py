import pytest
from constants import Endpoints
from utils.data_generator import DataGenerator

class TestMoviesPublic:
    def test_get_movie_by_id(self, api_manager, created_movie):
        resp = api_manager.movies_api.get_movie(created_movie)
        data = resp.json()
        assert data["id"] == created_movie
        assert 0 <= data["rating"] <= 5

    def test_get_movies_list_default(self, api_manager):
        resp = api_manager.movies_api.get_movies()
        data = resp.json()
        assert "movies" in data
        assert data["page"] == 1
        assert data["pageSize"] <= 20

    def test_get_movies_list_filters(self, api_manager, faker):
        params = {
            "pageSize": faker.random_int(min=1, max=20),
            "page": 1,
            "minPrice": 1,
            "maxPrice": 1000,
            "locations": ["MSK", "SPB"],
            "published": True,
            "genreId": 1
        }
        resp = api_manager.movies_api.get_movies(params=params)
        assert len(resp.json()["movies"]) <= params["pageSize"]

    def test_get_movie_not_found(self, api_manager):
        api_manager.movies_api.get_movie(999999, expected_status=404)

    def test_get_movies_invalid_page_size(self, api_manager):
        api_manager.movies_api.get_movies(params={"pageSize": 21}, expected_status=400)

class TestMoviesSuperAdmin:
    def test_create_movie_success(self, authorized_api_manager, created_genre, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),
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

    def test_create_movie_duplicate_name(self, authorized_api_manager, created_genre):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": 100,
            "description": "Test",
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": "https://test.com/img.jpg"
        }
        authorized_api_manager.movies_api.create_movie(payload)
        authorized_api_manager.movies_api.create_movie(payload, expected_status=409)

    def test_patch_movie(self, authorized_api_manager, created_movie, faker):
        payload = {"price": faker.random_int(min=100, max=999)}
        resp = authorized_api_manager.movies_api.edit_movie(created_movie, payload)
        assert resp.json()["price"] == payload["price"]

    def test_delete_movie(self, authorized_api_manager, api_manager, created_genre, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": faker.image_url()
        }
        movie_id = authorized_api_manager.movies_api.create_movie(payload).json()["id"]
        authorized_api_manager.movies_api.delete_movie(movie_id)
        api_manager.movies_api.get_movie(movie_id, expected_status=404)

class TestMoviesValidation:
    def test_create_movie_missing_required_field(self, authorized_api_manager, created_genre):
        payload = {
            "price": 100,
            "description": "no name",
            "location": "MSK",
            "published": True,
            "genreId": created_genre,
            "imageUrl": "https://test.com/img.jpg"
        }
        authorized_api_manager.movies_api.create_movie(payload, expected_status=400)

    def test_create_movie_invalid_genre(self, authorized_api_manager, faker):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": 100,
            "description": faker.sentence(),
            "location": "MSK",
            "published": True,
            "genreId": 999999,
            "imageUrl": faker.image_url()
        }
        authorized_api_manager.movies_api.create_movie(payload, expected_status=400)

class TestMoviesAuth:
    def test_create_movie_without_token_unauthorized(self, api_manager, created_genre):
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

    def test_patch_movie_without_token_unauthorized(self, api_manager, created_movie):
        api_manager.movies_api.edit_movie(created_movie, {"price": 777}, expected_status=401)

    def test_delete_movie_without_token_unauthorized(self, api_manager, created_movie):
        api_manager.movies_api.delete_movie(created_movie, expected_status=401)