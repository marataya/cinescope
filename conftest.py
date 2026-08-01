import pytest
import requests

from api.api_manager import ApiManager
from constants.roles import Roles
from entities.user import User
from models.test_user import TestUser
from resources.user_creds import SuperAdminCreds
from utils.data_generator import DataGenerator
from utils.db_client import DBClient


@pytest.fixture
def user_session():
    user_pool: list[ApiManager] = []
    def _create_user_session():
        session = requests.Session()
        mgr = ApiManager(session=session)
        user_pool.append(mgr)
        return mgr
    yield _create_user_session
    for mgr in user_pool:
        try:
            mgr.close_session()
        except:
            pass

@pytest.fixture
def api_manager(user_session):
    return user_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()
    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )
    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

# ============ BASE TEST USER ============
# test_user (TestUser random)
#   ├─ creation_user_data -> использует test_user.to_api_dict()
#   ├─ registered_user -> регистрирует test_user
#   │ └─ logged_in_user -> логинит registered_user
#   │ └─ authorized_api_manager
#   ├─ common_user -> создает test_user через super_admin
#   └─ test_admin_user (копия test_user с ADMIN)
#        └─ admin_user -> создает admin через super_admin
@pytest.fixture
def test_user() -> TestUser:
    """Базовая pydantic модель - единый источник данных"""
    pwd = DataGenerator.generate_valid_password()
    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=pwd,
        passwordRepeat=pwd,
        roles=[Roles.USER]
    )

@pytest.fixture
def test_admin_user(test_user) -> TestUser:
    """Копия test_user но с ролью ADMIN"""
    return test_user.model_copy(update={"roles": [Roles.ADMIN]})

# ============ REGISTRATION FLOW ============

@pytest.fixture
def creation_user_data(test_user: TestUser):
    """Для создания юзера через super_admin: POST /user"""
    data = test_user.to_api_dict()
    data["verified"] = True
    data["banned"] = False
    return data


@pytest.fixture
def registration_user_data(test_user: TestUser) -> TestUser:
    return test_user

@pytest.fixture
def registered_user(api_manager: ApiManager, test_user: TestUser):
    """Регистрирует test_user через /auth/register"""
    payload = test_user.to_api_dict()
    api_manager.auth_api.register_user(user_data=payload, expected_status=201)

    # возвращаем dict для совместимости со старыми тестами
    # которые делают registered_user["email"]
    result = payload.copy()
    result["email"] = test_user.email
    result["password"] = test_user.password
    result["fullName"] = test_user.fullName
    return result

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
    api_manager.auth_api.update_session_headers(
        Authorization=f"Bearer {logged_in_user['accessToken']}"
    )
    yield api_manager

# ============ MOVIES ============

@pytest.fixture
def created_genre(super_admin):
    payload = DataGenerator.generate_genre_payload()
    resp = super_admin.api.movies_api.send_request("POST", "/genres", data=payload, expected_status=201)
    genre_id = resp.json()["id"]
    yield genre_id
    super_admin.api.movies_api.send_request("DELETE", f"/genres/{genre_id}", expected_status=200)

@pytest.fixture
def created_movie(super_admin, created_genre):
    payload = DataGenerator.generate_movie_payload(genre_id=created_genre)
    resp = super_admin.api.movies_api.send_request("POST", "/movies", data=payload, expected_status=201)
    movie_id = resp.json()["id"]
    yield movie_id
    super_admin.api.movies_api.send_request("DELETE", f"/movies/{movie_id}", expected_status=200)

# ============ USERS WITH ROLES ============

@pytest.fixture
def common_user(user_session, super_admin, test_user: TestUser):
    """USER созданный через super_admin, зависит от test_user"""
    new_session = user_session()
    payload = test_user.model_copy(update={
        "roles": [Roles.USER],
        "verified": True,
        "banned": False
    }).model_dump(mode="json")

    # to_api_dict уже делает роли строками, но для /user нужен такой же формат
    payload["roles"] = [Roles.USER.value]

    common = User(test_user.email, test_user.password, [Roles.USER.value], new_session)
    super_admin.api.user_api.create_user(payload)
    common.api.auth_api.authenticate(common.creds)
    yield common
    try:
        users = super_admin.api.user_api.get_all_users()
        for u in users:
            if u["email"] == test_user.email:
                super_admin.api.user_api.delete_user(u["id"])
                break
    except Exception as e:
        print(f"common_user cleanup failed: {e}")

@pytest.fixture
def admin_user(user_session, super_admin, test_admin_user: TestUser):
    """ADMIN созданный через super_admin, зависит от test_admin_user -> test_user"""
    new_session = user_session()
    payload = test_admin_user.model_copy(update={
        "verified": True,
        "banned": False
    }).model_dump(mode="json")
    payload["roles"] = [Roles.ADMIN.value]

    admin = User(test_admin_user.email, test_admin_user.password, [Roles.ADMIN.value], new_session)
    super_admin.api.user_api.create_user(payload)
    admin.api.auth_api.authenticate(admin.creds)
    yield admin
    try:
        users = super_admin.api.user_api.get_all_users()
        for u in users:
            if u["email"] == test_admin_user.email:
                super_admin.api.user_api.delete_user(u["id"])
                break
    except Exception as e:
        print(f"admin_user cleanup failed: {e}")
        
@pytest.fixture
def db_client():
    client = DBClient()
    yield client
    client.close()
