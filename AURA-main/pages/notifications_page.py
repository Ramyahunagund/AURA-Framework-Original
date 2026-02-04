from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class NotificationsPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.table = '[data-testid="jarvis-notifications-table"]'
        self.elements.table_row = f"{self.elements.table} tr"
        self.elements.notifications_box = "[data-testid='portal-notifications-center']"
        self.elements.notifications_icon = "[data-testid='portal-notifications-button']"
        self.elements.notifications_table = "[data-testid='jarvis-notifications-table'], [data-testid='portal-notifications-center']"

    @property
    def table(self):
        return self.page.locator(self.elements.table).first
