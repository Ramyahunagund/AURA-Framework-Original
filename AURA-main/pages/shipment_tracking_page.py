from playwright.sync_api import Page
from core.utils import ElementsDict
from pages.base_page_object import BasePageObject

class ShipmentTrackingPage(BasePageObject):
    def __init__(self, page: Page):
        self.page = page
        self.elements = ElementsDict()
        self.elements.faq_question = '[data-testid="accordion"] button'
        self.elements.faq_answer1 = "#item-0"
        self.elements.faq_answer2 = "#item-1"
        self.elements.faq_answer3 = "#item-2"
        self.elements.faq_answer4 = "#item-3"
        self.elements.kCartridgeItem = "[data-testid='tracking-card-k']"
        self.elements.cCartridgeItem = "[data-testid='tracking-card-c']"
        self.elements.mCartridgeItem = "[data-testid='tracking-card-m']"
        self.elements.yCartridgeItem = "[data-testid='tracking-card-y']"
        self.elements.cmyCartridgeItem = "[data-testid='tracking-card-cmy']"
        self.elements.paper_tracking_item = '[class^="shippingTrackingSection__paper-card-container"]'
        self.elements.page_title = "#ink-shipment-ucde [data-testid='page-title']"
        self.elements.faq_card = "[data-testid='ink-shipment-jarvis-faq']"
        self.elements.faq_overview_link = "[data-testid='shipment-faq-2-plan-overview-link']"
        self.elements.faq_update_plan_link = "[data-testid='shipment-faq-2-change-plan-link']"
        self.elements.faq_recycle_link = "#item-3 a"
        self.elements.cartridge_support_card = "[class='cartridge-container']"
        self.elements.recycle_your_cartridge_link = "[data-testid='recycle-link']"
        self.elements.missing_ink_link = "[data-testid='missing-cartridge-link']"
        self.elements.table_date = "#date button"
        self.elements.table_description = "#description"
        self.elements.table_tracking_number = "#urlText"
        self.elements.table_selector = "[class^='historyTable__selector']"
        self.elements.table_selector_list = "[data-testid='history-table-select-options']"
        self.elements.shipment_history_table = "[data-testid='history-table-container']"
        self.elements.shipment_history_description = "[class*='activity-description']"
    
    def get_page_title(self, wait=60000):
        return self.page.wait_for_selector(self.elements.page_title, timeout=wait)
    
    def faq_question(self, index):
        """Returns the locator for a specific FAQ question by index (0-based)."""
        return self.page.locator(self.elements.faq_question).nth(index)
    
    def get_selector(self, name):
        if name in self.elements:
            return self.elements[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no selector '{name}'")
