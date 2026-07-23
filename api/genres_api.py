from constants import Endpoints
from custom_requester.custom_requester import CustomRequester


class GenresApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url="https://api.dev-cinescope.coconutqa.ru")

    def create_genre(self, genre_data: dict):
        return self.send_request("POST", Endpoints.GENRES, data=genre_data, expected_status=201).json()

    def delete_genre(self, genre_id: int):
        return self.send_request("DELETE", f"{Endpoints.GENRES}/{genre_id}", expected_status=200).json()