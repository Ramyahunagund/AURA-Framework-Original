from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class TermsOfServiceHPSmartPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.continue_button = "#full-screen-consent-form-footer-button-continue"
