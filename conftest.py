import pytest
import requests

from api.api_manager import ApiManager
from constants.roles import Roles
from entities.user import User
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator


@pytest.fixture
def api_manager(user_session):
    """Public client - no auth, for TestMoviesPublic"""
    return user_session()


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
def created_genre(super_admin):
    payload = DataGenerator.generate_genre_payload()
    resp = super_admin.api.movies_api.send_request(
        "POST", "/genres", data=payload, expected_status=201
    )
    genre_id = resp.json()["id"]
    yield genre_id
    super_admin.api.movies_api.send_request(
        "DELETE", f"/genres/{genre_id}", expected_status=200
    )

@pytest.fixture
def created_movie(super_admin, created_genre):
    payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
    resp = super_admin.api.movies_api.send_request(
        "POST", "/movies", data=payload, expected_status=201
    )
    movie_id = resp.json()["id"]
    yield movie_id
    super_admin.api.movies_api.send_request(
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
        try:
            user.close_session()
        except:
            pass

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
def test_user():
    return DataGenerator.generate_user_payload(is_admin_create=False)

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    test_user["verified"] = True
    test_user["banned"] = False
    test_user["roles"] = [Roles.USER.value]
    return test_user

@pytest.fixture
def common_user(user_session, super_admin):
    new_session = user_session()
    payload = DataGenerator.generate_user_payload(is_admin_create=True)
    payload["roles"] = [Roles.USER.value]
    payload["verified"] = True
    payload["banned"] = False

    common = User(payload['email'], payload['password'], [Roles.USER.value], new_session)
    super_admin.api.user_api.create_user(payload) # POST /user на AUTH_BASE_URL
    common.api.auth_api.authenticate(common.creds)
    yield common
    try:
        # GET /user возвращает список
        users_resp = super_admin.api.user_api.get_all_users()
        for u in users_resp:
            if u["email"] == payload["email"]:
                super_admin.api.user_api.delete_user(u["id"])
                break
    except Exception as e:
        print(f"common_user cleanup failed: {e}")

@pytest.fixture
def admin_user(user_session, super_admin):
    new_session = user_session()
    payload = DataGenerator.generate_user_payload(is_admin_create=True)
    payload["roles"] = [Roles.ADMIN.value]
    payload["verified"] = True
    payload["banned"] = False

    admin = User(payload['email'], payload['password'], [Roles.ADMIN.value], new_session)
    super_admin.api.user_api.create_user(payload)
    admin.api.auth_api.authenticate(admin.creds)
    yield admin
    try:
        users_resp = super_admin.api.user_api.get_all_users()
        for u in users_resp:
            if u["email"] == payload["email"]:
                super_admin.api.user_api.delete_user(u["id"])
                break
    except Exception as e:
        print(f"admin_user cleanup failed: {e}")