AUTH_BASE_URL = "https://auth.dev-cinescope.f5qa.ru"  # только логин
API_BASE_URL = "https://api.dev-cinescope.coconutqa.ru"  # вот тут все /movies, /genres

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

REGISTER_ENDPOINT = "/register"
LOGIN_ENDPOINT = "/login"

class Endpoints:
    MOVIES = "/movies"
    MOVIE_BY_ID = "/movies/{}"
    MOVIE_REVIEWS = "/movies/{}/reviews"
    MOVIE_REVIEW_HIDE = "/movies/{}/reviews/hide/{}"
    MOVIE_REVIEW_SHOW = "/movies/{}/reviews/show/{}"
    GENRES = "/genres"
    GENRE_BY_ID = "/genres/{}"


class Roles:
    PUBLIC = "PUBLIC"
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class Locations:
    MSK = "MSK"
    SPB = "SPB"