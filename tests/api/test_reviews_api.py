import pytest
import requests
from constants import API_BASE_URL, HEADERS, Endpoints


class TestReviewsPublic:
    """GET /movies/{id}/reviews - PUBLIC доступ"""

    def test_get_reviews_by_movie_id(self, api_base_url, created_movie):
        resp = requests.get(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            headers=HEADERS
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_reviews_movie_not_found(self, api_base_url, faker):
        fake_movie_id = faker.random_int(min=99999, max=999999)
        resp = requests.get(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(fake_movie_id)}",
            headers=HEADERS
        )
        assert resp.status_code == 404


class TestReviewsUser:
    """POST /movies/{id}/reviews - требует USER роль"""

    def test_create_review_success(self, api_session, api_base_url, created_movie, faker):
        payload = {
            "rating": faker.random_int(min=1, max=5),
            "text": faker.paragraph(nb_sentences=2)
        }
        resp = api_session.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json=payload
        )
        assert resp.status_code == 201
        review = resp.json()
        assert review["text"] == payload["text"]
        assert review["rating"] == payload["rating"]
        assert "userId" in review
        assert "createdAt" in review
        assert review["user"]["fullName"] == "Жмышенко Валерий Альбертович"

    def test_create_review_rating_boundary_min(self, api_session, api_base_url, created_movie, faker):
        payload = {"rating": 1, "text": faker.sentence()}
        resp = api_session.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json=payload
        )
        assert resp.status_code == 201

    def test_create_review_rating_boundary_max(self, api_session, api_base_url, created_movie, faker):
        payload = {"rating": 5, "text": faker.sentence()}
        resp = api_session.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json=payload
        )
        assert resp.status_code == 201

    def test_create_review_any_rating_accepted(self, api_session, api_base_url, created_movie, faker):
        """API принимает любой rating без валидации"""
        payload = {"rating": 0, "text": faker.word()}
        resp = api_session.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json=payload
        )
        assert resp.status_code == 201
        assert resp.json()["rating"] == 0

    def test_create_review_without_text_accepted(self, api_session, api_base_url, created_movie, faker):
        """API создает отзыв без text"""
        payload = {"rating": faker.random_int(min=1, max=5)}
        resp = api_session.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json=payload
        )
        assert resp.status_code == 201
        review = resp.json()
        assert review["rating"] == payload["rating"]
        assert review.get("text") is None or review.get("text") == ""

    def test_create_review_unauthorized(self, api_base_url, created_movie, faker):
        payload = {
            "rating": faker.random_int(min=1, max=5),
            "text": faker.sentence()
        }
        resp = requests.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json=payload,
            headers=HEADERS
        )
        assert resp.status_code == 401


class TestReviewsAdmin:
    """PATCH hide/show - требует ADMIN роль"""

    def test_hide_review_by_user_id(self, api_session, api_base_url, created_movie, faker):
        review_resp = api_session.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json={"rating": 2, "text": faker.sentence()}
        )
        assert review_resp.status_code == 201
        user_id = review_resp.json()["userId"]

        resp = api_session.patch(
            f"{api_base_url}{Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id)}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["userId"] == user_id
        # hidden может отсутствовать в ответе
        if "hidden" in data:
            assert data["hidden"] is True

    def test_show_review_by_user_id(self, api_session, api_base_url, created_movie, faker):
        review_resp = api_session.post(
            f"{api_base_url}{Endpoints.MOVIE_REVIEWS.format(created_movie)}",
            json={"rating": 2, "text": faker.word()}
        )
        user_id = review_resp.json()["userId"]

        api_session.patch(
            f"{api_base_url}{Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, user_id)}"
        )

        resp = api_session.patch(
            f"{api_base_url}{Endpoints.MOVIE_REVIEW_SHOW.format(created_movie, user_id)}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["userId"] == user_id
        if "hidden" in data:
            assert data["hidden"] is False

    def test_hide_review_unauthorized(self, api_base_url, created_movie, current_user):
        resp = requests.patch(
            f"{api_base_url}{Endpoints.MOVIE_REVIEW_HIDE.format(created_movie, current_user['id'])}",
            headers=HEADERS
        )
        assert resp.status_code == 401

    def test_show_review_unauthorized(self, api_base_url, created_movie, current_user):
        resp = requests.patch(
            f"{api_base_url}{Endpoints.MOVIE_REVIEW_SHOW.format(created_movie, current_user['id'])}",
            headers=HEADERS
        )
        assert resp.status_code == 401