from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class CancellationBannerPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.see_cancellation_timeline = "[data-testid='see-cancellation-timeline']"
        self.elements.keep_subscription_button = "[data-testid='cancellation-banner'] button"
        self.elements.cancellation_banner = "[data-testid='cancellation-banner']"
        # Subscription resume modal
        self.elements.resume_button = "[data-testid='confirm-subscription-resume-modal-content-resume-button']"
        self.elements.back_button = "[data-testid='confirm-subscription-resume-modal-content-back-button']"
        # Resume banner
        self.elements.resume_banner = "[data-testid='subscription-resumed-banner']"
