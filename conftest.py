import pytest
import requests

from api.api_manager import ApiManager
from constants.roles import Roles
from entities.user import User
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator


@pytest.fixture
def api_manager():
    """Чистая сессия для каждого теста"""
    session = requests.Session()
    yield ApiManager(session=session)
    session.close()

@pytest.fixture
def super_admin_api_manager():
    """Отдельная сессия с токеном админа"""
    session = requests.Session()
    manager = ApiManager(session=session)
    resp = manager.auth_api.login(
        credentials={"email": "api1@gmail.com", "password": "asdqwe123Q"},
        expected_status=201
    )
    token = resp.json()["accessToken"]
    manager.auth_api.update_session_headers(Authorization=f"Bearer {token}")
    yield manager
    session.close()

@pytest.fixture
def registered_user(api_manager):
    payload = DataGenerator.generate_user_payload()
    resp = api_manager.auth_api.register_user(user_data=payload, expected_status=201)
    user_data = resp.json()
    user_data["password"] = payload["password"]
    yield user_data

@pytest.fixture
def logged_in_user(api_manager, registered_user):
    resp = api_manager.auth_api.login(
        credentials={
            "email": registered_user["email"],
            "password": registered_user["password"]
        },
        expected_status=201
    )
    tokens = resp.json()
    tokens["user"] = registered_user
    yield tokens

@pytest.fixture
def authorized_api_manager(api_manager, logged_in_user):
    api_manager.auth_api.update_session_headers(Authorization=f"Bearer {logged_in_user['accessToken']}")
    yield api_manager

@pytest.fixture
def created_genre(super_admin_api_manager):
    payload = DataGenerator.generate_genre_payload()
    resp = super_admin_api_manager.movies_api.send_request(
        "POST", "/genres", data=payload, expected_status=201
    )
    genre_id = resp.json()["id"]
    yield genre_id
    super_admin_api_manager.movies_api.send_request(
        "DELETE", f"/genres/{genre_id}", expected_status=200
    )

@pytest.fixture
def created_movie(super_admin_api_manager, created_genre):
    payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
    resp = super_admin_api_manager.movies_api.send_request(
        "POST", "/movies", data=payload, expected_status=201
    )
    movie_id = resp.json()["id"]
    yield movie_id
    super_admin_api_manager.movies_api.send_request(
        "DELETE", f"/movies/{movie_id}", expected_status=200
    )

@pytest.fixture
def user_session():
    user_pool: list[ApiManager] = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session=session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session()

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        list(Roles.USER.value),
        new_session)

    super_admin.api.user_api.create_user(creation_user_data)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def test_user():
    return DataGenerator.generate_user_payload(is_admin_create=False)

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    # теперь test_user существует
    test_user["verified"] = True
    test_user["banned"] = False
    test_user["roles"] = ["USER"]
    return test_user