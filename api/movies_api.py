from custom_requester.custom_requester import CustomRequester
from constants import Endpoints

class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru")

    def get_movies(self, params=None, expected_status=200):
        return self.send_request("GET", Endpoints.MOVIES, params=params, expected_status=expected_status).json()

    def create_movie(self, data, expected_status=201):
        return self.send_request("POST", Endpoints.MOVIES, data=data, expected_status=expected_status).json()

    def get_movie(self, movie_id, expected_status=200):
        return self.send_request("GET", Endpoints.MOVIE_BY_ID.format(movie_id), expected_status=expected_status).json()

    def patch_movie(self, movie_id, data, expected_status=200):
        return self.send_request("PATCH", Endpoints.MOVIE_BY_ID.format(movie_id), data=data, expected_status=expected_status).json()

    def delete_movie(self, movie_id, expected_status=200):
        return self.send_request("DELETE", Endpoints.MOVIE_BY_ID.format(movie_id), expected_status=expected_status).json()

    def get_reviews(self, movie_id, expected_status=200):
        return self.send_request("GET", Endpoints.MOVIE_REVIEWS.format(movie_id), expected_status=expected_status).json()

    def create_review(self, movie_id, data, expected_status=201):
        return self.send_request("POST", Endpoints.MOVIE_REVIEWS.format(movie_id), data=data, expected_status=expected_status).json()

    def update_review(self, movie_id, data, expected_status=200):
        return self.send_request("PUT", Endpoints.MOVIE_REVIEWS.format(movie_id), data=data, expected_status=expected_status).json()

    def delete_review(self, movie_id, expected_status=200):
        return self.send_request("DELETE", Endpoints.MOVIE_REVIEWS.format(movie_id), expected_status=expected_status).json()