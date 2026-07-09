from custom_requester.custom_requester import CustomRequester

class MoviesAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru")

    def get_movies(self, params=None, expected_status=200, **kwargs):
        return self.send_request("GET", "/movies", params=params, expected_status=expected_status, **kwargs)

    def create_movie(self, movie_data, expected_status=201, **kwargs):
        return self.send_request("POST", "/movies", data=movie_data, expected_status=expected_status, **kwargs)

    def get_movie(self, movie_id, expected_status=200, **kwargs):
        return self.send_request("GET", f"/movies/{movie_id}", expected_status=expected_status, **kwargs)

    def edit_movie(self, movie_id, movie_data, expected_status=200, **kwargs):
        return self.send_request("PATCH", f"/movies/{movie_id}", data=movie_data, expected_status=expected_status, **kwargs)

    def delete_movie(self, movie_id, expected_status=200, **kwargs):
        return self.send_request("DELETE", f"/movies/{movie_id}", expected_status=expected_status, **kwargs)