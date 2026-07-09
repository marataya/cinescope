import pytest
from utils.data_generator import DataGenerator

class TestMoviesSuperAdmin:
    def test_create_movie_success(self, authorized_api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(created_genre)
        resp = authorized_api_manager.movies_api.create_movie(payload)
        movie_id = resp.json()["id"]
        authorized_api_manager.movies_api.delete_movie(movie_id)

    def test_create_movie_duplicate_name(self, authorized_api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(created_genre)
        authorized_api_manager.movies_api.create_movie(payload)
        authorized_api_manager.movies_api.create_movie(payload, expected_status=409)

    def test_patch_movie(self, authorized_api_manager, created_movie, faker):
        payload = {"price": faker.random_int(min=100, max=999)}
        resp = authorized_api_manager.movies_api.edit_movie(created_movie, payload)
        assert resp.json()["price"] == payload["price"]

    def test_delete_movie(self, authorized_api_manager, api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(created_genre)
        movie_id = authorized_api_manager.movies_api.create_movie(payload).json()["id"]
        authorized_api_manager.movies_api.delete_movie(movie_id)
        api_manager.movies_api.get_movie(movie_id, expected_status=404)

class TestMoviesValidation:
    def test_create_movie_missing_required_field(self, authorized_api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(created_genre)
        payload.pop("name")  # удаляем обязательное поле
        authorized_api_manager.movies_api.create_movie(payload, expected_status=400)

    def test_create_movie_invalid_genre(self, authorized_api_manager):
        payload = DataGenerator.generate_movie_payload(genre_id=999999)  # переопределяем
        authorized_api_manager.movies_api.create_movie(payload, expected_status=400)

class TestMoviesAuth:
    def test_create_movie_without_token_unauthorized(self, api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(created_genre)
        api_manager.movies_api.create_movie(payload, expected_status=401)

    def test_patch_movie_without_token_unauthorized(self, api_manager, created_movie):
        api_manager.movies_api.edit_movie(created_movie, {"price": 777}, expected_status=401)

    def test_delete_movie_without_token_unauthorized(self, api_manager, created_movie):
        api_manager.movies_api.delete_movie(created_movie, expected_status=401)