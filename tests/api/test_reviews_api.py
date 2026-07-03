import pytest
from constants import Endpoints
from utils.data_generator import DataGenerator


class TestReviewsPublic:
    def test_get_reviews_by_movie_id(self, public_requester, created_movie):
        resp = public_requester.send_request(
            "GET",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            expected_status=200
        )
        assert isinstance(resp.json(), list)

    def test_get_reviews_movie_not_found(self, public_requester, faker):
        fake_movie_id = faker.random_int(min=99999, max=999999)
        public_requester.send_request(
            "GET",
            Endpoints.MOVIE_REVIEWS.format(fake_movie_id),
            expected_status=404
        )


class TestReviewsUser:
    def test_create_review_success(self, api_requester, created_movie, faker):
        payload = {
            "rating": faker.random_int(min=1, max=5),
            "text": DataGenerator.generate_random_name()
        }
        resp = api_requester.send_request(
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
        assert "createdAt" in review

    def test_create_review_rating_zero_accepted(self, api_requester, created_movie):
        payload = {"rating": 0, "text": DataGenerator.generate_random_name()}
        resp = api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["rating"] == 0

    def test_create_review_rating_above_max_accepted(self, api_requester, created_movie):
        payload = {"rating": 6, "text": DataGenerator.generate_random_name()}
        resp = api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["rating"] == 6

    def test_create_review_without_text_accepted(self, api_requester, created_movie, faker):
        payload = {"rating": faker.random_int(min=1, max=5)}
        resp = api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        assert resp.json()["text"] is None

    def test_create_review_duplicate_conflict(self, api_requester, created_movie):
        payload = {"rating": 5, "text": "First"}
        api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=201
        )
        api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 1, "text": "Second"},
            expected_status=409
        )

    def test_edit_review(self, api_requester, created_movie):
        api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 3, "text": "Old"},
            expected_status=201
        )

        payload = {"rating": 5, "text": "Updated"}
        resp = api_requester.send_request(
            "PUT",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=200
        )
        assert resp.json()["rating"] == 5
        assert resp.json()["text"] == "Updated"

    def test_delete_review(self, api_requester, created_movie, current_user):
        api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 3, "text": "To delete"},
            expected_status=201
        )

        resp = api_requester.send_request(
            "DELETE",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            expected_status=200
        )
        assert resp.json()["userId"] == current_user["id"]

    def test_create_review_unauthorized(self, public_requester, created_movie):
        payload = {"rating": 5, "text": DataGenerator.generate_random_name()}
        public_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data=payload,
            expected_status=401
        )


class TestReviewsAdmin:
    def test_hide_review_returns_200(self, api_requester, created_movie):
        """PATCH /hide возвращает 200, поле hidden не возвращается в POST/GET"""
        review_resp = api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 2, "text": DataGenerator.generate_random_name()},
            expected_status=201
        )
        user_id = review_resp.json()["userId"]

        resp = api_requester.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id),
            expected_status=200
        )
        assert resp.json()["userId"] == user_id

    def test_show_review_returns_200(self, api_requester, created_movie):
        review_resp = api_requester.send_request(
            "POST",
            Endpoints.MOVIE_REVIEWS.format(created_movie),
            data={"rating": 2, "text": DataGenerator.generate_random_name()},
            expected_status=201
        )
        user_id = review_resp.json()["userId"]

        api_requester.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id),
            expected_status=200
        )
        resp = api_requester.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_SHOW.format(created_movie, user_id),
            expected_status=200
        )
        assert resp.json()["userId"] == user_id

    def test_hide_review_unauthorized(self, public_requester, created_movie, current_user):
        public_requester.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, current_user['id']),
            expected_status=401
        )

    def test_show_review_unauthorized(self, public_requester, created_movie, current_user):
        public_requester.send_request(
            "PATCH",
            Endpoints.MOVIE_REVIEW_SHOW.format(created_movie, current_user['id']),
            expected_status=401
        )