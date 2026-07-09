import random
import string
import time
from faker import Faker

faker = Faker()

class DataGenerator:
    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        timestamp = str(int(time.time() * 1000))
        return f"kek{random_string}{timestamp}@gmail.com"

    @staticmethod
    def generate_random_name():
        timestamp = str(int(time.time() * 1000))
        return f"{faker.first_name()} {faker.last_name()} {timestamp}"

    @staticmethod
    def generate_random_password():
        letters = random.choice(string.ascii_letters)
        digits = random.choice(string.digits)
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = random.randint(6, 18)
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)
        return ''.join(password)

    @staticmethod
    def generate_movie_payload(genre_id, **overrides):
        payload = {
            "name": DataGenerator.generate_random_name(),
            "price": faker.random_int(min=100, max=1000),
            "description": faker.text(max_nb_chars=200),
            "location": faker.random_element(["MSK", "SPB"]),
            "published": True,
            "genreId": genre_id,
            "imageUrl": faker.image_url()
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def generate_review_payload(**overrides):
        """Генератор тела отзыва. По дефолту rating=5, text=рандом"""
        payload = {
            "rating": faker.random_int(min=1, max=5),
            "text": faker.text(max_nb_chars=100)
        }
        payload.update(overrides)
        return payload