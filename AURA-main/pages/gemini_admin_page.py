from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class GeminiAdminPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.base_item_title = 'dl dt, .card-header'
        self.elements.base_item_content = 'dl dd, .card-body'
        self.elements.refund_payment_button = ".refund_payment_member_link > a"
