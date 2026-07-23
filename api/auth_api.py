from constants import AUTH_BASE_URL, Endpoints
from custom_requester.custom_requester import CustomRequester


class AuthApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def register_user(self, user_data, expected_status=201, **kwargs):
        return self.send_request("POST", Endpoints.REGISTER, data=user_data, expected_status=expected_status, **kwargs)

    def login_user(self, credentials, expected_status=201, **kwargs):
        return self.send_request("POST", Endpoints.LOGIN, data=credentials, expected_status=expected_status, **kwargs)