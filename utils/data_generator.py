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