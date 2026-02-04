from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class PrinterReplacementPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.printer_replacement_page = "[class^='printerReplacementPage__printer-replacement-page-container']"
        self.elements.printer_set_up_button = "[data-testid='printer-setup-button']"
        self.elements.printer_not_set_up_button = "[data-testid='no-printer-setup-button']"
        self.elements.printer_replacement_back_button = "[data-testid='printer-replacement-back-button']"
        self.elements.current_printer_card = '[data-testid="current-printer-card"]'
        self.elements.new_printer_card = '[data-testid="new-printer-card"]'
