import pytest
import requests
import logging
from faker import Faker
from api.api_manager import ApiManager
from constants import AUTH_BASE_URL, API_BASE_URL

logging.basicConfig(level=logging.INFO, format='%(message)s')

@pytest.fixture(scope="session")
def session():
    """HTTP-сессия для всех запросов"""
    http_session = requests.Session()
    yield http_session
    http_session.close()

@pytest.fixture(scope="session")
def api_manager(session):
    """Менеджер всех API классов"""
    return ApiManager(session)

@pytest.fixture(scope="session")
def valid_credentials():
    return {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

@pytest.fixture(scope="session")
def auth_data(api_manager, valid_credentials):
    """Логинимся 1 раз на сессию"""
    resp = api_manager.auth_api.login_user(valid_credentials, expected_status=201)
    return resp.json()

@pytest.fixture(scope="session")
def bearer_token(auth_data):
    return auth_data["accessToken"]

@pytest.fixture(scope="session")
def current_user(auth_data):
    return auth_data["user"]

@pytest.fixture
def api_requester(bearer_token):
    """Реквестер для API с токеном"""
    from custom_requester.custom_requester import CustomRequester
    session = requests.Session()
    requester = CustomRequester(session, API_BASE_URL)
    requester.update_session_headers(Authorization=f"Bearer {bearer_token}")
    return requester

@pytest.fixture
def public_requester():
    """Реквестер для публичных ручек"""
    from custom_requester.custom_requester import CustomRequester
    session = requests.Session()
    return CustomRequester(session, API_BASE_URL)

@pytest.fixture
def created_genre(api_requester, faker):
    payload = {"name": faker.word().capitalize() + " " + faker.word()}
    resp = api_requester.send_request("POST", "/genres", data=payload, expected_status=201)
    genre_id = resp.json()["id"]
    yield genre_id
    api_requester.send_request("DELETE", f"/genres/{genre_id}", expected_status=200, need_logging=False)

@pytest.fixture
def created_movie(api_requester, created_genre, faker):
    payload = {
        "name": faker.sentence(nb_words=3)[:-1],
        "price": faker.random_int(min=100, max=1000),
        "description": faker.text(max_nb_chars=200),
        "location": faker.random_element(["MSK", "SPB"]),
        "published": True,
        "genreId": created_genre,
        "imageUrl": faker.image_url()
    }
    resp = api_requester.send_request("POST", "/movies", data=payload, expected_status=201)
    movie_id = resp.json()["id"]
    yield movie_id
    api_requester.send_request("DELETE", f"/movies/{movie_id}", expected_status=200, need_logging=False)