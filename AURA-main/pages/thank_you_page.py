from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class ThankYouPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.continue_button = "[data-testid='continue-button']"
        self.elements.thank_you_card = "[data-testid='thank-you-step'] [class^='styles__RightSection']"
        self.elements.close_modal_finish_printer_replacement = '.vn-modal--footer > div> button'
        self.elements.email = "[class^='styles__Email-']"
        self.elements.cartridge_image = "[class^='styles__Cartridge-']"
        self.elements.subtitle = "[class^='styles__InfoCardSubtitle-']"