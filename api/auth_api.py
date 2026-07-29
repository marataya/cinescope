from constants.endpoints import Endpoints
from constants.urls import AUTH_BASE_URL
from custom_requester.custom_requester import CustomRequester

try:
    from resources.user_creds import SuperAdminCreds
    def _default_creds():
        return SuperAdminCreds.USERNAME, SuperAdminCreds.PASSWORD
except:
    from utils.data import USERNAME, PASSWORD
    def _default_creds():
        return (USERNAME, PASSWORD)

class AuthApi(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)

    def register_user(self, user_data, expected_status=201, **kwargs):
        # Добавь конвертацию TestUser -> dict
        if hasattr(user_data, "to_api_dict"):
            user_data = user_data.to_api_dict()
        elif hasattr(user_data, "model_dump"):
            user_data = user_data.model_dump()

        return self.send_request(
            method="POST",
            endpoint=Endpoints.REGISTER,
            data=user_data,
            expected_status=expected_status,
            **kwargs
        )

    def login_user(self, credentials=None, expected_status=201, **kwargs):
        # поддержка всех вариантов вызова:
        # login_user(data), login_user(credentials=data), login_user(creds=data), login_user(data=...)

        # вытаскиваем из kwargs если передали другими именами
        if credentials is None:
            credentials = kwargs.pop("credentials", None) or kwargs.pop("creds", None) or kwargs.pop("data", None)

        if credentials is None:
            # вызов без аргументов -> дефолтный суперадмин
            credentials = _default_creds()

        if isinstance(credentials, (list, tuple)):
            credentials = {"email": credentials[0], "password": credentials[1]}

        return self.send_request(
            method="POST",
            endpoint=Endpoints.LOGIN,
            data=credentials,
            expected_status=expected_status,
            **kwargs
        )

    def login(self, creds=None, expected_status=201, **kwargs):
        if creds is None:
            creds = kwargs.pop("credentials", None) or kwargs.pop("creds", None) or kwargs.pop("data", None)

        if creds is None:
            return self.login_user(None, expected_status=expected_status, **kwargs)

        if isinstance(creds, (list, tuple)):
            data = {"email": creds[0], "password": creds[1]}
        else:
            data = creds
        return self.login_user(data, expected_status=expected_status, **kwargs)

    def authenticate(self, creds=None, expected_status=201, **kwargs):
        return self.login(creds, expected_status=expected_status, **kwargs)