from constants.endpoints import Endpoints
from constants.urls import AUTH_BASE_URL
from custom_requester.custom_requester import CustomRequester

class UserApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def create_user(self, user_data, expected_status=201):
        return self.send_request(
            "POST",
            Endpoints.USERS,
            data=user_data,
            expected_status=expected_status
        ).json()

    def get_user(self, user_id, expected_status=200):
        return self.send_request(
            "GET",
            Endpoints.USER_BY_ID.format(user_id),
            expected_status=expected_status
        ).json()

    def delete_user(self, user_id, expected_status=200):
        # DELETE возвращает пустой body, нельзя .json()
        response = self.send_request(
            "DELETE",
            Endpoints.USER_BY_ID.format(user_id),
            expected_status=expected_status
        )
        # если тело пустое - возвращаем {}
        try:
            return response.json()
        except:
            return {}