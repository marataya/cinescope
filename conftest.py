import pytest
import requests
import logging
from custom_requester.custom_requester import CustomRequester
from constants import AUTH_BASE_URL, API_BASE_URL, LOGIN_ENDPOINT

logging.basicConfig(level=logging.INFO, format='%(message)s')

@pytest.fixture(scope="session")
def api_base_url():
    return API_BASE_URL

@pytest.fixture(scope="session")
def auth_base_url():
    return AUTH_BASE_URL

@pytest.fixture(scope="session")
def valid_credentials():
    return {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

@pytest.fixture(scope="session")
def auth_data(auth_base_url, valid_credentials):
    session = requests.Session()
    requester = CustomRequester(session, auth_base_url)
    resp = requester.send_request("POST", LOGIN_ENDPOINT, data=valid_credentials, expected_status=201)
    return resp.json()

@pytest.fixture(scope="session")
def bearer_token(auth_data):
    return auth_data["accessToken"]

@pytest.fixture(scope="session")
def current_user(auth_data):
    return auth_data["user"]

@pytest.fixture
def api_requester(bearer_token):
    session = requests.Session()
    requester = CustomRequester(session, API_BASE_URL)
    requester.update_session_headers(Authorization=f"Bearer {bearer_token}")
    return requester

@pytest.fixture
def public_requester():
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