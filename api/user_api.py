from constants import AUTH_BASE_URL, Endpoints
from custom_requester.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def get_users(self, expected_status=200, **kwargs):
        return self.send_request("GET", Endpoints.USERS, expected_status=expected_status, **kwargs)

    def get_user(self, user_id, expected_status=200, **kwargs):
        return self.send_request("GET", Endpoints.USER_BY_ID.format(user_id), expected_status=expected_status, **kwargs)