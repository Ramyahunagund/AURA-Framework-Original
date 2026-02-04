from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class PrinterSelectionPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.printer_selection_page = "[data-testid='printer-selection-step']"
        self.elements.printer_radio_button = "[data-testid^='printer-card']"
        self.elements.printer_radio_button_input = "[data-testid^='printer-card'] input"
        self.elements.continue_button = "[data-testid='continue-button']"
        self.elements.add_printer = "[data-testid='add-printer-card']"
        self.elements.printer_image = "[class='printer-image-container'] img"
        self.elements.printer_serial = "[class='printer-details']"
        self.elements.printer_benefits = "[class^='styles__PrinterBenefitsContent'] p"
        self.elements.add_printer_image = "[class='printer-image-container'] svg"
        self.elements.add_printer_title = "[class='printer-text'] h5"
        self.elements.add_printer_body = "[data-testid='printer-card-add'] .printer-text p"
        self.elements.add_printer_check = "[data-testid='printer-card-add'] .radio-button"
        self.elements.arrow_back_button = "[class*='slick-prev left arrow-button']"
        self.elements.arrow_next_button = "[class*='slick-next right arrow-butto']"
        self.elements.printer_offline_message = "[class*='styles__ErrorMessage'] > p"
        self.elements.connectivity_guide_link = "[class*='styles__ConnectivityGuide']"
