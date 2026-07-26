import random
import string
import uuid

from faker import Faker

fake = Faker("ru_RU") # <- у тебя fake

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

    @staticmethod
    def generate_user_payload(is_admin_create=False):
        pwd = DataGenerator.generate_valid_password()
        # используем fake а не faker
        payload = {
            "email": fake.email(),
            "password": pwd,
            "passwordRepeat": pwd,
            "fullName": fake.name(),
            "verified": True,
            "banned": False,
            "roles": ["USER"]
        }
        # для /register бэк не принимает verified/banned/roles
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
            "location": fake.random_element(["MSK", "SPB"]),
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