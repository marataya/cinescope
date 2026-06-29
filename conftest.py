import pytest
import requests
from faker import Faker

from constants import AUTH_BASE_URL, API_BASE_URL, HEADERS, LOGIN_ENDPOINT

fake = Faker("ru_RU")


@pytest.fixture(scope="session")
def api_base_url():
    return API_BASE_URL


@pytest.fixture(scope="session")
def auth_base_url():
    return AUTH_BASE_URL


@pytest.fixture(scope="session")
def valid_credentials():
    """Креды для api1@gmail.com у которого есть все роли"""
    return {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }


@pytest.fixture(scope="session")
def auth_data(auth_base_url, valid_credentials):
    """Логинимся 1 раз на сессию, возвращаем весь ответ"""
    resp = requests.post(
        f"{auth_base_url}{LOGIN_ENDPOINT}",
        json=valid_credentials,
        headers=HEADERS
    )
    assert resp.status_code == 201, f"Login failed: {resp.text}"
    data = resp.json()
    assert "accessToken" in data, "No accessToken in response"
    assert "refreshToken" in data, "No refreshToken in response"
    return data


@pytest.fixture(scope="session")
def bearer_token(auth_data):
    """Только accessToken"""
    return auth_data["accessToken"]


@pytest.fixture(scope="session")
def current_user(auth_data):
    """Данные юзера из ответа логина"""
    return auth_data["user"]


@pytest.fixture
def auth_headers(bearer_token):
    """Заголовки с Bearer токеном"""
    return {**HEADERS, "Authorization": f"Bearer {bearer_token}"}


@pytest.fixture
def api_session(auth_headers):
    """requests.Session с проставленным токеном для API"""
    session = requests.Session()
    session.headers.update(auth_headers)
    return session


@pytest.fixture
def created_genre(api_session, api_base_url, faker):
    """Создает жанр перед тестом, удаляет после"""
    payload = {"name": faker.word().capitalize() + " " + faker.word()}
    resp = api_session.post(f"{api_base_url}/genres", json=payload)
    assert resp.status_code == 201
    genre_id = resp.json()["id"]

    yield genre_id

    api_session.delete(f"{api_base_url}/genres/{genre_id}")


@pytest.fixture
def created_movie(api_session, api_base_url, created_genre, faker):
    """Создает фильм перед тестом, удаляет после"""
    payload = {
        "name": faker.sentence(nb_words=3)[:-1],
        "price": faker.random_int(min=100, max=1000),
        "description": faker.text(max_nb_chars=200),
        "location": faker.random_element(["MSK", "SPB"]),
        "published": True,
        "genreId": created_genre,
        "imageUrl": faker.image_url()
    }
    resp = api_session.post(f"{api_base_url}/movies", json=payload)
    assert resp.status_code == 201
    movie_id = resp.json()["id"]

    yield movie_id

    api_session.delete(f"{api_base_url}/movies/{movie_id}")