import random
import string
import uuid

from faker import Faker

fake = Faker("ru_RU")

class DataGenerator:

    @staticmethod
    def generate_valid_password():
        letters = string.ascii_letters
        digits = string.digits
        special = "?@#$%^&*_+-()[]{}><\\|\"'.,:;"

        password = [
            random.choice(letters),
            random.choice(digits)
        ]
        length = random.randint(8, 12)
        all_chars = letters + digits + special
        password += [random.choice(all_chars) for _ in range(length - 2)]
        random.shuffle(password)
        return ''.join(password)

    # ========== NEW METHODS FOR TestUser model ==========

    @staticmethod
    def generate_random_email():
        # уникальность через uuid
        return f"{uuid.uuid4().hex[:8]}_{fake.email()}"

    @staticmethod
    def generate_random_name():
        return fake.name()

    # alias который ты использовал раньше
    @staticmethod
    def generate_random_password():
        return DataGenerator.generate_valid_password()

    # ========== EXISTING METHODS ==========

    @staticmethod
    def generate_user_payload(is_admin_create=False):
        pwd = DataGenerator.generate_valid_password()
        payload = {
            "email": DataGenerator.generate_random_email(),
            "password": pwd,
            "passwordRepeat": pwd,
            "fullName": DataGenerator.generate_random_name(),
            "verified": True,
            "banned": False,
            "roles": ["USER"]
        }
        if not is_admin_create:
            payload.pop("verified", None)
            payload.pop("banned", None)
            payload.pop("roles", None)

        return payload

    @staticmethod
    def generate_genre_payload():
        return {"name": f"{fake.word().capitalize()} {uuid.uuid4().hex[:6]}"}

    @staticmethod
    def generate_movie_payload(genre_id):
        return {
            "name": f"{fake.word().capitalize()} {uuid.uuid4().hex[:6]}",
            "price": fake.random_int(min=100, max=1000),
            "description": fake.text(max_nb_chars=200),
            "location": fake.random_element(elements=["MSK", "SPB"]),
            "published": True,
            "genreId": genre_id,
            "imageUrl": fake.image_url()
        }

    @staticmethod
    def generate_review_payload(rating=None):
        return {
            "rating": rating if rating is not None else fake.random_int(min=0, max=5),
            "text": fake.text(max_nb_chars=100)
        }

    @staticmethod
    def generate_movie_filter_payload():
        """Для параметризованных тестов фильтров"""
        return {
            "minPrice": fake.random_int(min=1, max=400),
            "maxPrice": fake.random_int(min=500, max=1000),
            "locations": fake.random_element(elements=["MSK", "SPB"]),
            "genreId": 1,
            "pageSize": 10,
            "page": 1
        }

    # ======== TRANSACTIONAL TESTS ===============
    @staticmethod
    def generate_random_int(max_val: int = 10000):
        return random.randint(1, max_val)

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())