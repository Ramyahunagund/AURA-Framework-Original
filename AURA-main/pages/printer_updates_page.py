from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class PrinterUpdatesPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page.set_default_timeout(60000)
        # Page elements
        self.elements.continue_button = "[data-testid='btn-continue']"

    def accept_automatic_updates(self):
        try:
            self.continue_button.click()
        except Exception as e:
            print(f"Automatic updates continue button not found or could not be clicked: {e}")
