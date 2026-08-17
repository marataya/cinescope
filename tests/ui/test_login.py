import time

import allure
import pytest
from playwright.sync_api import Page, expect

from constants.urls import UI_BASE_URL


@allure.title("UI тест логина")
@pytest.mark.slow
def test_cinescope_login(login_page, page: Page):
    login_page.login("api1@gmail.com", "asdqwe123Q")

    error_message = page.get_by_text("Что-то пошло не так").first
    page.wait_for_load_state(state="networkidle")
    expect(error_message).to_be_visible()

    page.goto(UI_BASE_URL)
    page.reload()

    expect(page.locator("button", has_text="Профиль")).to_be_visible()
    expect(page.locator("button", has_text="Профиль")).to_be_enabled()

    time.sleep(3)