import random
import re
import string
import uuid

from faker import Faker

fake = Faker("ru_RU")

class DataGenerator:

    @staticmethod
    def generate_valid_password():
        # гарантируем: 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол
        upper = random.choice(string.ascii_uppercase)
        lower = random.choice(string.ascii_lowercase)
        digit = random.choice(string.digits)
        special = random.choice("?@#$%^&*_+-")

        length = random.randint(8, 12)
        all_chars = string.ascii_letters + string.digits + "?@#$%^&*_+-()[]{}><"
        rest = [random.choice(all_chars) for _ in range(length - 4)]

        password = [upper, lower, digit, special] + rest
        random.shuffle(password)
        return ''.join(password)

    # @staticmethod
    # def generate_valid_password():
    #     letters = string.ascii_letters
    #     digits = string.digits
    #     special = "?@#$%^&*_+-()[]{}><"
    #     password = [random.choice(letters), random.choice(digits)]
    #     length = random.randint(8, 12)
    #     all_chars = letters + digits + special
    #     password += [random.choice(all_chars) for _ in range(length - 2)]
    #     random.shuffle(password)
    #     return ''.join(password)

    @staticmethod
    def generate_random_email():
        # Только валидный формат, без подчеркивания перед @ и без двойных @
        return f"{uuid.uuid4().hex[:8].lower()}@test.com"

    @staticmethod
    def generate_random_name():
        # Берем first + last и вычищаем все кроме букв
        first = re.sub(r'[^A-Za-zА-Яа-яЁё]', '', fake.first_name())
        last = re.sub(r'[^A-Za-zА-Яа-яЁё]', '', fake.last_name())
        # на случай если faker вернул пустое после очистки
        if not first: first = "Ivan"
        if not last: last = "Ivanov"
        return f"{first} {last}"

    @staticmethod
    def generate_random_password():
        return DataGenerator.generate_valid_password()

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
            "imageUrl": "https://example.com/poster.jpg" # fake.image_url() иногда дает невалидный url для бэка
        }

    @staticmethod
    def generate_review_payload(rating=None):
        return {
            "rating": rating if rating is not None else fake.random_int(min=1, max=5), # 0 нельзя
            "text": fake.text(max_nb_chars=100)
        }

    @staticmethod
    def generate_movie_filter_payload():
        return {
            "minPrice": fake.random_int(min=1, max=400),
            "maxPrice": fake.random_int(min=500, max=1000),
            "locations": fake.random_element(elements=["MSK", "SPB"]),
            "genreId": 1,
            "pageSize": 10,
            "page": 1
        }

    @staticmethod
    def generate_random_int(max_val: int = 10000):
        return random.randint(1, max_val)

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())