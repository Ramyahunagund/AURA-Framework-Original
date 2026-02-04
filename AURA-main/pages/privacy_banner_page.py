from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class PrivacyBannerPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.accept_button = "#onetrust-accept-btn-handler"

    def accept_privacy_banner(self):
        try:
            self.accept_button.click()
        except Exception as e:
            print(f"Privacy banner not found or could not be accepted: {e}")