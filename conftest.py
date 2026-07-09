import pytest
import requests
import logging
from faker import Faker
from api.api_manager import ApiManager
from utils.data_generator import DataGenerator

logging.basicConfig(level=logging.INFO, format='%(message)s')

@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """Публичный ApiManager без токена"""
    return ApiManager(session)

@pytest.fixture(scope="session")
def valid_credentials():
    return {"email": "api1@gmail.com", "password": "asdqwe123Q"}

@pytest.fixture(scope="session")
def auth_data(api_manager, valid_credentials):
    resp = api_manager.auth_api.login_user(valid_credentials, expected_status=201)
    return resp.json()

@pytest.fixture(scope="session")
def bearer_token(auth_data):
    return auth_data["accessToken"]

@pytest.fixture(scope="session")
def current_user(auth_data):
    return auth_data["user"]

@pytest.fixture
def authorized_api_manager(session, bearer_token):
    """ApiManager с токеном SUPER_ADMIN"""
    auth_session = requests.Session()
    auth_session.headers.update(session.headers)
    auth_session.headers.update({"Authorization": f"Bearer {bearer_token}"})
    yield ApiManager(auth_session)
    auth_session.close()

@pytest.fixture
def created_genre(authorized_api_manager):
    payload = {"name": DataGenerator.generate_random_name()}
    resp = authorized_api_manager.movies_api.send_request(
        "POST", "/genres", data=payload, expected_status=201
    )
    genre_id = resp.json()["id"]
    yield genre_id
    authorized_api_manager.movies_api.send_request(
        "DELETE", f"/genres/{genre_id}", expected_status=200, need_logging=False
    )

@pytest.fixture
def created_movie(authorized_api_manager, created_genre, faker):
    payload = {
        "name": DataGenerator.generate_random_name(),
        "price": faker.random_int(min=100, max=1000),
        "description": faker.text(max_nb_chars=200),
        "location": faker.random_element(["MSK", "SPB"]),
        "published": True,
        "genreId": created_genre,
        "imageUrl": faker.image_url()
    }
    resp = authorized_api_manager.movies_api.create_movie(payload)
    movie_id = resp.json()["id"]
    yield movie_id
    authorized_api_manager.movies_api.delete_movie(movie_id)
