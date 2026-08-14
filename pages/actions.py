from xml.sax.xmlreader import Locator

import allure
from playwright.sync_api import Page


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста в поле: {locator}")
    def enter_text(self, locator: Locator, text: str):
        locator.fill(text)

    @allure.step("Клик по элементу: {locator}")
    def click(self, locator: Locator):
        locator.click()