import time

import allure
import pytest
from playwright.sync_api import Page, expect

from utils.data_generator import DataGenerator


@allure.title("UI тест регистрации")
@pytest.mark.slow
def test_registration(register_page, page: Page):
    email = DataGenerator().generate_random_email()
    # email = f".{randint(1, 999999)}@email.qa"

    register_page.register("Иван Иванов", email, "qwerty123Q")
    # Для примера. Так-то уже есть фикстуры и генератор данных
    expect(page.get_by_text("Подтвердите свою почту")).to_be_visible()
    time.sleep(5)