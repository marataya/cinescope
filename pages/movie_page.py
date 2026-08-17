from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage
import allure

class CinescopeMoviePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.review_text_input: Locator = page.get_by_test_id("movie_review_input")
        self.rating_combobox: Locator = page.locator('button[role="combobox"]').filter(has=page.get_by_test_id("movie_rating_select"))
        self.review_submit_button: Locator = page.get_by_test_id("movie_review_submit_button")
        if self.review_submit_button.count() == 0:
            self.review_submit_button = page.locator('button:has-text("Оставить отзыв"), button:has-text("Отправить")').first

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

    def _get_review_container(self, text: str) -> Locator:
        # Ищем параграф с текстом отзыва и берем его родителя - карточку отзыва
        # Это работает и когда отзыв в <li> и когда в <div>
        text_loc = self.page.get_by_text(text, exact=True).first
        # ближайший контейнер который содержит и кнопку меню
        return text_loc.locator("xpath=ancestor::div[contains(@class,'card') or contains(@class,'border')][1]").first if text_loc.count() > 0 else self.page.locator(f"div:has-text('{text}')").first

    @allure.step("Удалить отзыв: {text}")
    def delete_review(self, text: str):
        # 1. Находим карточку по тексту отзыва (надежно, не через listitem)
        review_text = self.page.get_by_text(text, exact=True).first
        expect(review_text).to_be_visible(timeout=10000)

        # 2. Кнопка меню находится рядом с именем автора - ищем в том же контейнере
        # В снапшоте: heading "Назарова..." + button + paragraph: text
        # Значит берем родителя на 2 уровня выше
        container = review_text.locator("xpath=..").locator("..")
        # fallback - ищем кнопку в радиусе 200px от текста
        menu_button = container.get_by_role("button").first
        if menu_button.count() == 0:
            menu_button = self.page.locator(f"div:has-text('{text}')").get_by_role("button").first

        menu_button.click()

        # 3. Пункт меню Удалить
        delete_item = self.page.get_by_role("menuitem", name="Удалить")
        expect(delete_item).to_be_visible(timeout=5000)
        delete_item.click()

    def get_review_by_text(self, text: str) -> Locator:
        # Самый надежный локатор - просто по тексту
        return self.page.get_by_text(text, exact=True).first