from playwright.sync_api import Page
from pages.base_page_object import BasePageObject
import test_flows_common.test_flows_common as common

class SignInPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.email_input = "#username"
        self.elements.use_password_button = "#user-name-form-submit"
        self.elements.password_input = "#password"
        self.elements.sign_in_button = "#sign-in"
