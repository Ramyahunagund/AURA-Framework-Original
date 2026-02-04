from playwright.sync_api import Page

from core.settings import framework_logger
from pages.base_page_object import BasePageObject

class PlanSelectorV3Page(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.plans_selector_v3 = "[data-testid='plans-selector-v3-combobox']"
        self.elements.plans_listbox_v3 = "[role='listbox']"
        self.elements.plan_option = "[role='option']"
        self.elements.ink_paper_button = "[data-testid='select-plan-ink-and-paper']"
        self.elements.ink_only_button = "[data-testid='select-plan-ink-only']"
        self.elements.content_area_v3 = "[data-testid='v3-content-area']"
        self.elements.continue_button = "[data-testid='consumer-plans-select-plans'] span"

        #header elements
        self.elements.virtual_agent_link = "[data-testid='virtual-agent-link']"
        self.elements.support_phone_number_link = "[data-testid='support-phone-number-link']"
        self.elements.country_selector_button = "[data-testid='country-selector-button']"
        self.elements.account_button = "[data-testid='account-button']"

        self.elements.pay_as_you_print_plan_card = '[data-testid="i_pay_as_you_print-type-card-content-container"]'
        self.elements.monthly_plan_card = '[data-testid="i_ink-type-card-content-container"]'

    def select_plan(self, plan_value: str):
        # option_selector = f'{self.elements.plan_option}:has-text("({plan_value}")' # Could not locate when 'plan value' is 10
        option_selector = f'//*[@role="option" and contains(normalize-space(.),"{plan_value} ")]'
        framework_logger.info(f"Selecting plan option with selector: {option_selector}")
        self.page.locator(option_selector).click()
        framework_logger.info(f"plan selection clicked successfully from Dropdown Box")
