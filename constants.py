# Base URLs
BASE_URL = "https://api.dev-cinescope.coconutqa.ru"
AUTH_BASE_URL = "https://auth.dev-cinescope.f5qa.ru"

class Endpoints:
    # Auth
    REGISTER = "/register"
    LOGIN = "/login"
    REFRESH_TOKENS = "/refresh-tokens"
    LOGOUT = "/logout"
    USERS_ME = "/users/me"

    # User management
    USERS = "/user"
    USER_BY_ID = "/user/{}"

    # Movies
    MOVIES = "/movies"
    MOVIE_BY_ID = "/movies/{}"
    MOVIE_REVIEWS = "/movies/{}/reviews"
    MOVIE_REVIEW_HIDE = "/movies/{}/reviews/hide/{}"
    MOVIE_REVIEW_SHOW = "/movies/{}/reviews/show/{}"

    # Genres
    GENRES = "/genres"
    GENRE_BY_ID = "/genres/{}"