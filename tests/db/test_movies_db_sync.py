import allure

from models.movie_response import MovieResponse
from utils.data_generator import DataGenerator

@allure.epic("Movies DB Sync")
class TestMovieDbSync:

    @allure.title("Жизненный цикл фильма: создание через API -> проверка в БД -> удаление через API -> проверка удаления из БД")
    def test_movie_lifecycle_db_sync(self, super_admin, db_helper, created_genre):
        # Генерим уникальные данные
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
        movie_name = payload["name"]

        # 1. ДО - в базе отсутствует фильм
        assert db_helper.get_movie_by_name(movie_name) is None, f"Фильм {movie_name} уже есть в БД до теста"
        assert db_helper.movie_exists_by_name(movie_name) is False

        # 2. Создание через API
        resp = super_admin.api.movies_api.send_request(
            "POST", "/movies", data=payload, expected_status=201
        )
        # movie_id = resp.json()["id"]
        # created_movie_name = resp.json()["name"]
        movie_response = MovieResponse(**resp.json())
        movie_id = movie_response.id
        created_movie_name = movie_response.name

        try:
            # 3. ПОСЛЕ СОЗДАНИЯ - в базе появился фильм
            db_movie = db_helper.get_movie_by_id(movie_id)
            assert db_movie is not None, "Фильм не появился в БД после POST /movies"
            assert db_movie.id == movie_id
            assert db_movie.name == movie_name == created_movie_name
            assert db_movie.genre_id == created_genre
            assert db_movie.price == payload["price"]
            assert db_movie.published == payload["published"]

            # доп проверка через name
            assert db_helper.movie_exists(movie_id) is True
            assert db_helper.get_movie_by_name(movie_name).id == movie_id

        finally:
            # 4. Удаление через API
            super_admin.api.movies_api.send_request(
                "DELETE", f"/movies/{movie_id}", expected_status=200
            )

        # 5. ПОСЛЕ УДАЛЕНИЯ - в базе также удаляется
        assert db_helper.get_movie_by_id(movie_id) is None, \
            "Фильм остался в БД после DELETE /movies"
        assert db_helper.get_movie_by_name(movie_name) is None
        assert db_helper.movie_exists(movie_id) is False