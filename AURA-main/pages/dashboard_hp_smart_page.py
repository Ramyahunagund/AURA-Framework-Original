from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class DashboardHPSmartPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.signup_now_button = "[data-testid='get-started-button']"
        self.elements.promotional_page_background = '[id^="promotionalPage__promotional-page-container-parity"]'
        self.elements.promotional_page_disclaimer = '[class^="promotionalPage__disclaimer-container"]'
        self.elements.keypoint_intelligence_link = '[data-testid="savings-ink-keypoint-link-footnote"]'
        self.elements.shipping_billing_page = '.monetization__shipping-billing-management-react'
        
        # Footer elements
        self.elements.footer_hp_com_link = '[data-testid="footer-hp-com"]'
        self.elements.footer_wireless_print_center_link = '[data-testid="footer-wireless-print-center"]'
        self.elements.footer_help_center_link = '[data-testid="footer-help-center"]'
        self.elements.footer_terms_of_use_link = '[data-testid="footer-terms-of-use"]'
        self.elements.footer_hp_privacy_link = '[data-testid="footer-hp-privacy"]'
        self.elements.footer_hp_your_privacy_choices_link = '[data-testid="footer-hp-your-privacy-choices"]'
        
        # Additional element mappings
        self.elements.subscription_state = '[data-testid="subscription-state"], [data-testid="ii-enrollment-status-printers-pp"]'
        self.elements.enroll_hp_instant_ink_link = 'text=Enroll in HP Instant Ink'
        self.elements.printer_options = '[aria-controls="printerOptions"], [aria-controls="printer-options-data"]'
        self.elements.update_plan_link = '[data-testid="update-plan-pp"]'
        self.elements.remove_printer_link = '[data-testid="remove-printer-options-pp"]'
        self.elements.printers_page_title = '[data-testid="printers-title-pp"]'
        self.elements.print_plans_page = '[id^="promotionalPage__promotional-page-container-parity"]'
