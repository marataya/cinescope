from playwright.sync_api import Page, Locator

from pages.base_page import BasePage


class CinescopeLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.url = f"{self.home_url}/login"

        self.email_input: Locator = page.get_by_test_id("login_email_input")
        self.password_input: Locator = page.get_by_test_id("login_password_input")
        self.submit_button: Locator = page.get_by_test_id("login_submit_button")

    def open(self):
        self.open_url(self.url)

    def login(self, email: str, password: str):
        self.enter_text(self.email_input, email)
        self.enter_text(self.password_input, password)
        self.click(self.submit_button)
