import allure
from playwright.sync_api import Page, Locator, expect

from pages.base_page import BasePage


class CinescopeMoviePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.review_text_input: Locator = page.get_by_test_id("movie_review_input")
        self.rating_combobox: Locator = page.locator('button[role="combobox"]').filter(has=page.get_by_test_id("movie_rating_select"))
        self.review_action_buttons: Locator = page.get_by_test_id("movie_review_actions_button")
        self.review_submit_button: Locator = page.get_by_test_id("movie_review_submit_button")

    def open(self, movie_id):
        self.open_url(f"{self.home_url}/movies/{movie_id}")

    @allure.step("Добавить отзыв {rating}/5")
    def add_review(self, text: str, rating: int):
        expect(self.review_text_input).to_be_visible(timeout=10000)
        self.enter_text(self.review_text_input, text)
        self.click(self.rating_combobox)
        option = self.page.get_by_role("option", name=str(rating), exact=True)
        expect(option).to_be_visible()
        self.click(option)
        self.click(self.review_submit_button)
        # ждем пока появится в DOM
        self.page.wait_for_timeout(500)


    @allure.step("Удалить отзыв: {text}")
    def delete_review(self, text: str):
        # 1. Находим карточку по тексту отзыва (надежно, не через listitem)
        review_text = self.page.get_by_text(text, exact=True).first
        expect(review_text).to_be_visible(timeout=10000)

        self.review_action_buttons.click()

        delete_item = self.page.get_by_role("menuitem", name="Удалить")
        expect(delete_item).to_be_visible(timeout=5000)
        delete_item.click()

    def get_review_by_text(self, text: str) -> Locator:
        # Самый надежный локатор - просто по тексту
        return self.page.get_by_text(text, exact=True).first