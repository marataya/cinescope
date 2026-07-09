import allure
import pytest

from constants import Endpoints
from utils.data_generator import DataGenerator, fake


@allure.epic("Movies API")
class TestMoviesPublic:
    @allure.title("Получение списка фильмов с пагинацией по умолчанию")
    def test_get_movies_default_pagination(self, api_manager):
        resp = api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIES,
            expected_status=200
        )
        data = resp.json()
        assert "movies" in data
        assert "count" in data
        assert "page" in data
        assert "pageSize" in data
        assert "pageCount" in data
        assert len(data["movies"]) <= 10  # default pageSize
        assert data["page"] == 1

    @allure.title("Фильтрация фильмов по цене и локации")
    @pytest.mark.parametrize("min_price, max_price, locations", [
        (100, 300, ["MSK"]),
        (200, 500, ["SPB"]),
        (1, 1000, ["MSK", "SPB"]),
    ])
    def test_get_movies_by_filter(self, api_manager, min_price, max_price, locations):
        params = {
            "minPrice": min_price,
            "maxPrice": max_price,
            "locations": locations,
            "pageSize": 20
        }

        resp = api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIES,
            params=params,
            expected_status=200
        )
        data = resp.json()
        movies = data["movies"]

        assert len(movies) <= params["pageSize"], "Превышен pageSize"

        for movie in movies:
            assert min_price <= movie["price"] <= max_price, \
                f"Цена {movie['price']} вне диапазона {min_price}-{max_price}, id={movie['id']}"

            assert movie["location"] in locations, \
                f"Локация {movie['location']} не входит в {locations}, id={movie['id']}"

            assert movie["published"] is True, f"Фильм id={movie['id']} не опубликован"

    @allure.title("Получение фильма по ID")
    def test_get_movie_by_id(self, api_manager, created_movie):
        resp = api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIE_BY_ID.format(created_movie),
            expected_status=200
        )
        data = resp.json()
        assert data["id"] == created_movie
        assert "reviews" in data
        assert "genre" in data
        assert "rating" in data

    @allure.title("Получение фильма по несуществующему ID")
    def test_get_movie_not_found(self, api_manager):
        api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIE_BY_ID.format(999999),
            expected_status=404
        )


@allure.epic("Movies API")
class TestMoviesSuperAdmin:
    @allure.title("Удаление фильма")
    def test_delete_movie(self, super_admin_api_manager):
        # Создаем жанр
        genre_payload = DataGenerator.generate_genre_payload()
        genre_resp = super_admin_api_manager.movies_api.send_request(
            "POST", "/genres", data=genre_payload, expected_status=201
        )
        genre_id = genre_resp.json()["id"]

        # Создаем фильм
        movie_payload = DataGenerator.generate_movie_payload(genre_id=genre_id)
        movie_resp = super_admin_api_manager.movies_api.send_request(
            "POST", "/movies", data=movie_payload, expected_status=201
        )
        movie_id = movie_resp.json()["id"]

        # Удаляем
        super_admin_api_manager.movies_api.send_request(
            "DELETE", f"/movies/{movie_id}", expected_status=200
        )

        # Проверяем что удален
        super_admin_api_manager.movies_api.send_request(
            "GET", f"/movies/{movie_id}", expected_status=404
        )

        # Чистим жанр
        super_admin_api_manager.movies_api.send_request(
            "DELETE", f"/genres/{genre_id}", expected_status=200
        )

    @allure.title("Обновление фильма")
    def test_patch_movie(self, super_admin_api_manager, created_movie):
        # created_movie можно использовать, т.к. мы не удаляем в тесте
        new_price = fake.random_int(min=100, max=1000)
        resp = super_admin_api_manager.movies_api.send_request(
            "PATCH",
            f"/movies/{created_movie}",
            data={"price": new_price},
            expected_status=200
        )
        assert resp.json()["price"] == new_price

    @allure.title("Создание фильма")
    def test_create_movie(self, super_admin_api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
        resp = super_admin_api_manager.movies_api.send_request(
            "POST", "/movies", data=payload, expected_status=201
        )
        data = resp.json()
        assert data["name"] == payload["name"]
        # Чистим за собой
        super_admin_api_manager.movies_api.send_request(
            "DELETE", f"/movies/{data['id']}", expected_status=200
        )

    @allure.title("Создание фильма дубликат")
    def test_create_movie_duplicate_name_conflict(self, super_admin_api_manager, created_movie):
        # Получаем существующий фильм
        resp = super_admin_api_manager.movies_api.send_request(
            "GET", f"/movies/{created_movie}", expected_status=200
        )
        existing = resp.json()

        payload = DataGenerator.generate_movie_payload(genre_id=existing["genreId"])
        payload["name"] = existing["name"]

        super_admin_api_manager.movies_api.send_request(
            "POST", "/movies", data=payload, expected_status=409
        )

@allure.epic("Reviews API")
class TestReviewsPublic:
    @allure.title("Получение отзывов фильма")
    def test_get_reviews_by_movie_id(self, api_manager, created_movie):
        resp = api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            expected_status=200
        )
        assert isinstance(resp.json(), list)

    @allure.title("Получение отзывов несуществующего фильма")
    def test_get_reviews_movie_not_found(self, api_manager):
        api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIE_REVIEWS.format(985439),
            expected_status=404
        )


@allure.epic("Reviews API")
class TestReviewsUser:
    @allure.title("Создание отзыва USER")
    def test_create_review_success(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        data = resp.json()
        assert data["rating"] == payload["rating"]
        assert data["text"] == payload["text"]
        assert "userId" in data
        assert "user" in data
        assert data["user"]["fullName"]

    @allure.title("Создание отзыва с rating=0")
    def test_create_review_rating_zero_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=0)
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["rating"] == 0

    @allure.title("Создание отзыва с rating > 5")
    def test_create_review_rating_above_max_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=6)
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["rating"] == 6

    @allure.title("Создание отзыва без текста")
    def test_create_review_without_text_accepted(self, authorized_api_manager, created_movie):
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 3},
            expected_status=201
        )
        assert resp.json()["rating"] == 3
        assert resp.json()["text"] is None

    @allure.title("Повторное создание отзыва - конфликт")
    def test_create_review_duplicate_conflict(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=409
        )

    @allure.title("Редактирование своего отзыва")
    def test_edit_review(self, authorized_api_manager, created_movie):
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 3, "text": "Old"},
            expected_status=201
        )
        resp = authorized_api_manager.movies_api.send_request(
            "PUT",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 5, "text": "Updated"},
            expected_status=200
        )
        assert resp.json()["rating"] == 5
        assert resp.json()["text"] == "Updated"
        assert resp.json()["hidden"] is False

    @allure.title("Удаление своего отзыва")
    def test_delete_review(self, authorized_api_manager, created_movie):
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 3, "text": "To delete"},
            expected_status=201
        )
        resp = authorized_api_manager.movies_api.send_request(
            "DELETE",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            expected_status=200
        )
        assert resp.json()["text"] == "To delete"

    @allure.title("Создание отзыва без авторизации")
    def test_create_review_unauthorized(self, api_manager, created_movie):
        api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(),
            expected_status=401
        )