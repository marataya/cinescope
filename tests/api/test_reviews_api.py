import pytest
from constants import Endpoints
from utils.data_generator import DataGenerator


class TestReviewsPublic:
    def test_get_reviews_by_movie_id(self, api_manager, created_movie):
        resp = api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            expected_status=200
        )
        assert isinstance(resp.json(), list)

    def test_get_reviews_movie_not_found(self, api_manager, faker):
        fake_movie_id = faker.random_int(min=99999, max=999999)
        api_manager.movies_api.send_request(
            "GET",
            Endpoints.MOVIE_REVIEWS.format(fake_movie_id),
            expected_status=404
        )


class TestReviewsUser:
    def test_create_review_success(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        review = resp.json()
        assert review["rating"] == payload["rating"]
        assert review["text"] == payload["text"]
        assert "userId" in review
        assert "user" in review

    def test_create_review_rating_zero_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=0)
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["rating"] == 0

    def test_create_review_rating_above_max_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=6)
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["rating"] == 6

    def test_create_review_without_text_accepted(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload()
        payload.pop("text")
        resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["text"] is None

    def test_create_review_duplicate_conflict(self, authorized_api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=5, text="First")
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(rating=1, text="Second"),
            expected_status=409
        )

    def test_edit_review(self, authorized_api_manager, created_movie):
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(rating=3, text="Old"),
            expected_status=201
        )

        payload = DataGenerator.generate_review_payload(rating=5, text="Updated")
        resp = authorized_api_manager.movies_api.send_request(
            "PUT",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=200
        )
        assert resp.json()["rating"] == 5
        assert resp.json()["text"] == "Updated"

    def test_delete_review(self, authorized_api_manager, created_movie, current_user):
        authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(rating=3, text="To delete"),
            expected_status=201
        )

        resp = authorized_api_manager.movies_api.send_request(
            "DELETE",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            expected_status=200
        )
        assert resp.json()["userId"] == current_user["id"]

    def test_create_review_unauthorized(self, api_manager, created_movie):
        payload = DataGenerator.generate_review_payload(rating=5)
        api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=401
        )


class TestReviewsAdmin:
    def test_hide_review_returns_200(self, authorized_api_manager, created_movie):
        review_resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(rating=2),
            expected_status=201
        )
        user_id = review_resp.json()["userId"]

        resp = authorized_api_manager.movies_api.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id),
            expected_status=200
        )
        assert resp.json()["userId"] == user_id

    def test_show_review_returns_200(self, authorized_api_manager, created_movie):
        review_resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(rating=2),
            expected_status=201
        )
        user_id = review_resp.json()["userId"]

        authorized_api_manager.movies_api.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id),
            expected_status=200
        )
        resp = authorized_api_manager.movies_api.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_SHOW.format(created_movie, user_id),
            expected_status=200
        )
        assert resp.json()["userId"] == user_id

    def test_hide_review_unauthorized(self, authorized_api_manager, api_manager, created_movie):
        # Сначала создаем отзыв чтобы был валидный userId
        review_resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(),
            expected_status=201
        )
        user_id = review_resp.json()["userId"]

        # Пытаемся скрыть без токена - должен быть 401, а не 404
        api_manager.movies_api.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id),
            expected_status=401
        )

    def test_show_review_unauthorized(self, authorized_api_manager, api_manager, created_movie):
        review_resp = authorized_api_manager.movies_api.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=DataGenerator.generate_review_payload(),
            expected_status=201
        )
        user_id = review_resp.json()["userId"]

        authorized_api_manager.movies_api.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id),
            expected_status=200
        )

        api_manager.movies_api.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_SHOW.format(created_movie, user_id),
            expected_status=401
        )