import allure
import pytest
from models.movie import MovieResponse
from utils.data_generator import DataGenerator, fake


@allure.epic("Movies API")
class TestMoviesPublic:
    @allure.title("Получение списка фильмов с пагинацией по умолчанию")
    def test_get_movies_default_pagination(self, api_manager):
        data = api_manager.movies_api.get_movies()

        assert "movies" in data
        assert "count" in data
        assert len(data["movies"]) <= 10
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
        data = api_manager.movies_api.get_movies(params=params)
        movies = data["movies"]

        for movie in movies:
            assert min_price <= movie["price"] <= max_price
            assert movie["location"] in locations
            assert movie["published"] is True

    @allure.title("Получение фильма по ID")
    def test_get_movie_by_id(self, api_manager, created_movie):
        data = api_manager.movies_api.get_movie(created_movie)

        assert data["id"] == created_movie
        assert "reviews" in data
        assert "genre" in data

    @allure.title("Получение фильма по несуществующему ID")
    def test_get_movie_not_found(self, api_manager):
        api_manager.movies_api.get_movie(999999, expected_status=404)


@allure.epic("Movies API")
class TestMoviesSuperAdmin:
    @allure.title("Удаление фильма")
    def test_delete_movie(self, super_admin_api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
        movie = super_admin_api_manager.movies_api.create_movie(payload)
        movie_id = movie["id"]

        super_admin_api_manager.movies_api.delete_movie(movie_id)
        super_admin_api_manager.movies_api.get_movie(movie_id, expected_status=404)

    @allure.title("Обновление фильма")
    def test_patch_movie(self, super_admin_api_manager, created_movie):
        new_price = fake.random_int(min=100, max=1000)

        updated = super_admin_api_manager.movies_api.patch_movie(
            created_movie, {"price": new_price}
        )

        assert updated["price"] == new_price

    @allure.title("Создание фильма")
    def test_create_movie(self, super_admin_api_manager, created_genre):
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)

        movie = super_admin_api_manager.movies_api.create_movie(payload)
        validated = MovieResponse(**movie)

        assert validated.name == payload["name"]
        assert validated.price == payload["price"]
        assert validated.genreId == created_genre
        assert validated.published == payload["published"]
        assert validated.description == payload["description"]
        assert validated.location == payload["location"]
        assert validated.rating == 0

        super_admin_api_manager.movies_api.delete_movie(validated.id)

    @allure.title("Создание фильма дубликат")
    def test_create_movie_duplicate_name_conflict(self, super_admin_api_manager, created_movie):
        existing = super_admin_api_manager.movies_api.get_movie(created_movie)

        payload = DataGenerator.generate_movie_payload(genre_id=existing["genreId"])
        payload["name"] = existing["name"]

        super_admin_api_manager.movies_api.create_movie(payload, expected_status=409)


@allure.epic("Reviews API")
class TestReviewsPublic:
    @allure.title("Получение отзывов фильма")
    def test_get_reviews_by_movie_id(self, api_manager, created_movie):
        reviews = api_manager.movies_api.get_reviews(created_movie)
        assert isinstance(reviews, list)

    @allure.title("Получение отзывов несуществующего фильма")
    def test_get_reviews_movie_not_found(self, api_manager):
        api_manager.movies_api.get_reviews(985439, expected_status=404)


@allure.epic("Reviews API")
class TestReviewsUser:
    @allure.title("Создание отзыва USER")
    def test_create_review_success(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()

        review = authorized_api_manager.movies_api.create_review(created_movie, payload)

        assert review["rating"] == payload["rating"]
        assert review["text"] == payload["text"]
        assert "userId" in review
        assert review["user"]["fullName"]

    @allure.title("Создание отзыва с rating=0")
    def test_create_review_rating_zero_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=0)
        review = authorized_api_manager.movies_api.create_review(created_movie, payload)
        assert review["rating"] == 0

    @allure.title("Создание отзыва с rating > 5")
    def test_create_review_rating_above_max_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=6)
        review = authorized_api_manager.movies_api.create_review(created_movie, payload)
        assert review["rating"] == 6

    @allure.title("Создание отзыва без текста")
    def test_create_review_without_text_accepted(self, authorized_api_manager, created_movie):
        review = authorized_api_manager.movies_api.create_review(created_movie, {"rating": 3})
        assert review["rating"] == 3
        assert review["text"] is None

    @allure.title("Повторное создание отзыва - конфликт")
    def test_create_review_duplicate_conflict(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()
        authorized_api_manager.movies_api.create_review(created_movie, payload)
        authorized_api_manager.movies_api.create_review(created_movie, payload, expected_status=409)

    @allure.title("Редактирование своего отзыва")
    def test_edit_review(self, authorized_api_manager, created_movie):
        authorized_api_manager.movies_api.create_review(created_movie, {"rating": 3, "text": "Old"})

        updated = authorized_api_manager.movies_api.update_review(
            created_movie, {"rating": 5, "text": "Updated"}
        )

        assert updated["rating"] == 5
        assert updated["text"] == "Updated"
        assert updated["hidden"] is False

    @allure.title("Удаление своего отзыва")
    def test_delete_review(self, authorized_api_manager, created_movie):
        authorized_api_manager.movies_api.create_review(created_movie, {"rating": 3, "text": "To delete"})

        deleted = authorized_api_manager.movies_api.delete_review(created_movie)
        assert deleted["text"] == "To delete"

    @allure.title("Создание отзыва без авторизации")
    def test_create_review_unauthorized(self, api_manager, created_movie):
        api_manager.movies_api.create_review(
            created_movie, DataGenerator.generate_review_payload(), expected_status=401
        )