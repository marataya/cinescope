from custom_requester.custom_requester import CustomRequester
from constants.endpoints import Endpoints


class MoviesApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru")

    def get_movies(self, params=None, expected_status=200):
        return self.send_request("GET", Endpoints.MOVIES, params=params, expected_status=expected_status).json()

    def get_movie(self, movie_id, expected_status=200):
        return self.send_request("GET", f"{Endpoints.MOVIES}/{movie_id}", expected_status=expected_status).json()
        # используй f-string чтобы не зависеть от.format

    def create_movie(self, data, expected_status=201):
        return self.send_request("POST", Endpoints.MOVIES, data=data, expected_status=expected_status).json()

    def delete_movie(self, movie_id, expected_status=200):
        resp = self.send_request("DELETE", f"{Endpoints.MOVIES}/{movie_id}", expected_status=expected_status)
        try:
            return resp.json()
        except:
            return resp

    def patch_movie(self, movie_id, data, expected_status=200):
        return self.send_request("PATCH", f"{Endpoints.MOVIES}/{movie_id}", data=data, expected_status=expected_status).json()

    def get_reviews(self, movie_id, expected_status=200):
        return self.send_request("GET", f"{Endpoints.MOVIES}/{movie_id}/reviews", expected_status=expected_status).json()

    def create_review(self, movie_id, data, expected_status=201):
        return self.send_request("POST", f"{Endpoints.MOVIES}/{movie_id}/reviews", data=data, expected_status=expected_status).json()

    def update_review(self, movie_id, data, expected_status=200):
        return self.send_request("PUT", f"{Endpoints.MOVIES}/{movie_id}/reviews", data=data, expected_status=expected_status).json()

    def delete_review(self, movie_id, expected_status=200):
        return self.send_request("DELETE", f"{Endpoints.MOVIES}/{movie_id}/reviews", expected_status=expected_status).json()