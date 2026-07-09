import random
import string
import uuid

from faker import Faker

fake = Faker("ru_RU")


class DataGenerator:
    @staticmethod
    def generate_valid_password():
        # Regex: /^(?=.*[a-zA-Zа-яА-Я])(?=.*\d)[a-zA-Zа-яА-Я\d?@#$%^&*_+\-()\[\]{}><\\\/|"'.,:;]{8,20}$/
        # Важно: ё и Ё НЕ входят в а-яА-Я
        letters = string.ascii_letters
        digits = string.digits
        special = "?@#$%^&*_+-()[]{}><\\|\"'.,:;"

        password = [
            random.choice(letters),  # минимум 1 буква
            random.choice(digits)  # минимум 1 цифра
        ]
        length = random.randint(8, 12)
        all_chars = letters + digits + special
        password += [random.choice(all_chars) for _ in range(length - 2)]
        random.shuffle(password)
        return ''.join(password)

    @staticmethod
    def generate_user_payload():
        password = DataGenerator.generate_valid_password()
        return {
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": password,
            "passwordRepeat": password,
            "fullName": fake.name()
        }

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