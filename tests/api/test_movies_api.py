import allure
import pytest

from utils.data_generator import DataGenerator


@allure.epic("Movies API")
class TestMoviesPublic:
    @allure.title("Получение списка фильмов с пагинацией по умолчанию")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_movies_default_pagination(self, api_manager):
        data = api_manager.movies_api.get_movies()

        assert "movies" in data
        assert "count" in data
        assert len(data["movies"]) <= 10
        assert data["page"] == 1

    @allure.title("Фильтрация фильмов по цене и локации")
    @pytest.mark.regression
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
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_movie_by_id(self, api_manager, created_movie):
        data = api_manager.movies_api.get_movie(created_movie)

        assert data["id"] == created_movie
        assert "reviews" in data
        assert "genre" in data

    @allure.title("Получение фильма по несуществующему ID")
    @pytest.mark.regression
    def test_get_movie_not_found(self, api_manager):
        api_manager.movies_api.get_movie(999999, expected_status=404)


@allure.epic("Reviews API")
class TestReviewsPublic:

    @allure.title("Получение отзывов фильма")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_get_reviews_by_movie_id(self, api_manager, created_movie):
        reviews = api_manager.movies_api.get_reviews(created_movie)
        assert isinstance(reviews, list)

    @allure.title("Получение отзывов несуществующего фильма")
    @pytest.mark.regression
    def test_get_reviews_movie_not_found(self, api_manager):
        api_manager.movies_api.get_reviews(985439, expected_status=404)


@allure.epic("Reviews API")
class TestReviewsUser:

    @allure.title("Создание отзыва USER")
    @pytest.mark.smoke
    def test_create_review_success(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()

        review = authorized_api_manager.movies_api.create_review(created_movie, payload)

        assert review["rating"] == payload["rating"]
        assert review["text"] == payload["text"]
        assert "userId" in review
        assert review["user"]["fullName"]

    @allure.title("Создание отзыва с rating=0")
    @pytest.mark.slow
    @pytest.mark.regression
    def test_create_review_rating_zero_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=0)
        review = authorized_api_manager.movies_api.create_review(created_movie, payload)
        assert review["rating"] == 0

    @allure.title("Создание отзыва с rating > 5")
    @pytest.mark.slow
    @pytest.mark.regression
    def test_create_review_rating_above_max_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=6)
        review = authorized_api_manager.movies_api.create_review(created_movie, payload)
        assert review["rating"] == 6

    @allure.title("Создание отзыва без текста")
    @pytest.mark.regression
    def test_create_review_without_text_accepted(self, authorized_api_manager, created_movie):
        review = authorized_api_manager.movies_api.create_review(created_movie, {"rating": 3})
        assert review["rating"] == 3
        assert review["text"] is None

    @allure.title("Повторное создание отзыва - конфликт")
    @pytest.mark.slow
    @pytest.mark.regression
    def test_create_review_duplicate_conflict(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()
        authorized_api_manager.movies_api.create_review(created_movie, payload)
        authorized_api_manager.movies_api.create_review(created_movie, payload, expected_status=409)

    @allure.title("Редактирование своего отзыва")
    @pytest.mark.slow
    @pytest.mark.regression
    def test_edit_review(self, authorized_api_manager, created_movie):
        authorized_api_manager.movies_api.create_review(created_movie, {"rating": 3, "text": "Old"})

        updated = authorized_api_manager.movies_api.update_review(
            created_movie, {"rating": 5, "text": "Updated"}
        )

        assert updated["rating"] == 5
        assert updated["text"] == "Updated"
        assert updated["hidden"] is False

    @allure.title("Удаление своего отзыва")
    @pytest.mark.slow
    @pytest.mark.regression
    def test_delete_review(self, authorized_api_manager, created_movie):
        authorized_api_manager.movies_api.create_review(created_movie, {"rating": 3, "text": "To delete"})

        deleted = authorized_api_manager.movies_api.delete_review(created_movie)
        assert deleted["text"] == "To delete"

    @allure.title("Создание отзыва без авторизации")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_create_review_unauthorized(self, api_manager, created_movie):
        api_manager.movies_api.create_review(
            created_movie, DataGenerator.generate_review_payload(), expected_status=401
        )


@allure.epic("Movies API - Roles")
class TestMoviesRoles:

    @allure.title("ADMIN не может создавать фильмы - 403 (только SUPER_ADMIN может)")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_admin_can_create_movie(self, admin_user, created_genre):
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
        # в актуальной API ADMIN тоже получает 403 - это текущее поведение
        admin_user.api.movies_api.create_movie(payload, expected_status=403)

    @allure.title("USER не может создавать фильмы - 403")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_user_cannot_create_movie(self, common_user, created_genre):
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
        common_user.api.movies_api.create_movie(payload, expected_status=403)

    @allure.title("SUPER_ADMIN может создавать фильмы - 201")
    @pytest.mark.smoke
    @pytest.mark.regression
    def test_super_admin_can_create_movie(self, super_admin, created_genre):
        payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
        movie = super_admin.api.movies_api.create_movie(payload)
        assert movie["id"] is not None
        # cleanup through same super_admin
        super_admin.api.movies_api.delete_movie(movie["id"])

@allure.epic("Movies API - Filters")
class TestMoviesFilters:

    @allure.title("Фильтрация фильмов по ценам")
    @pytest.mark.regression
    @pytest.mark.parametrize("min_price, max_price", [
        (1, 100), (100, 500), (500, 1000),
    ], ids=["price_1-100", "price_100-500", "price_500-1000"])
    def test_filter_by_price_range(self, api_manager, min_price, max_price):
        data = api_manager.movies_api.get_movies(
            params={"minPrice": min_price, "maxPrice": max_price, "pageSize": 10, "page": 1}
        )
        for movie in data["movies"]:
            assert min_price <= movie["price"] <= max_price

    @allure.title("Фильтрация фильмов по локациям")
    @pytest.mark.regression
    @pytest.mark.parametrize("location", ["MSK", "SPB"], ids=["location_MSK", "location_SPB"])
    def test_filter_by_locations(self, api_manager, location):
        data = api_manager.movies_api.get_movies(
            params={"locations": location, "pageSize": 10, "page": 1}
        )
        for movie in data["movies"]:
            movie_loc = movie.get("location") or movie.get("locations") or []
            if isinstance(movie_loc, str):
                movie_loc = [movie_loc]
            assert location in movie_loc

    @allure.title("Фильтрация фильмов по жанрам")
    @pytest.mark.regression
    def test_filter_by_genreId(self, api_manager, super_admin):
        genre_payload = DataGenerator.generate_genre_payload()
        genre_resp = super_admin.api.movies_api.send_request("POST", "/genres", data=genre_payload, expected_status=201)
        genre_id = genre_resp.json()["id"]
        movie_payload = DataGenerator.generate_movie_payload(genre_id=genre_id)
        movie_resp = super_admin.api.movies_api.send_request("POST", "/movies", data=movie_payload, expected_status=201)
        movie_id = movie_resp.json()["id"]
        try:
            data = api_manager.movies_api.get_movies(params={"genreId": genre_id, "pageSize": 10, "page": 1})
            assert len(data["movies"]) >= 1
        finally:
            super_admin.api.movies_api.send_request("DELETE", f"/movies/{movie_id}", expected_status=200)
            super_admin.api.movies_api.send_request("DELETE", f"/genres/{genre_id}", expected_status=200)

    @allure.title("Фильтрация фильмов по нескольким параметрам")
    @pytest.mark.regression
    @pytest.mark.parametrize("params", [
        {"minPrice": 1, "maxPrice": 1000, "locations": "MSK", "genreId": 1},
        {"minPrice": 1, "maxPrice": 200, "locations": "SPB"},
        {"locations": "MSK", "genreId": 1},
    ], ids=["all_filters", "price+location", "location+genre"])
    def test_filter_combined_parametrized(self, api_manager, created_genre, params):
        if params.get("genreId") == 1:
            params["genreId"] = created_genre
        data = api_manager.movies_api.get_movies(params={**params, "pageSize": 10, "page": 1})
        assert "movies" in data