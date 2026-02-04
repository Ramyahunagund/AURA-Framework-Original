from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class PrintersPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.printer_online = '[data-testid="internet-connection-status-pp-ps"] [aria-label="Check Circle"]'
        self.elements.printer_options = '[data-testid="printer-options-pp"]'
        self.elements.remove_printer_button = '[data-testid="remove-printer-options-pp"]'
        self.elements.enroll_in_instant_ink = '[data-testid="enroll-II-pp"]'
        self.elements.enrolled_printer_box = '[class^="styles__PrinterBox-@jarvis/react-hpx-devices"]:has([data-testid="printer-supplies"])'
        self.elements.non_enrolled_printer_box = '[class^="styles__PrinterBox-@jarvis/react-hpx-devices"]:has([data-testid="enroll-II-pp"])'
        self.elements.confirm_remove_printer_button = '[data-testid="button_1"]'
        self.elements.close_remove_printer_button = '[data-testid="button_0"]'
        self.elements.manage_subscription_button = '[data-testid="button_1"]'
