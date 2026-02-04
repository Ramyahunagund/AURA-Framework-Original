from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class ChangePlanCancellationPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Change Plan modal
        self.elements.change_plan_link = '[class^="changePlanModalContent__change-plan-container"]'
        #self.elements.return_to_cancellation_button = '[data-testid="return-to-cancellation"]'
        self.elements.return_to_cancellation_button = 'xpath=//*[text()="Return to Cancellation"]'
        self.elements.change_plan_modal = '[class^="changePlanModalContent__change-plan-container"]'
        self.elements.change_plan_title = '[class^="changePlanModalContent__change-plan-header-content_"] h3'
        self.elements.change_plan_subtitle = '[class^="changePlanModalContent__change-plan-header-content_"]>p'
        self.elements.change_plan_icon = '[class^="changePlanModalContent__change-cancel-info-icon"]'
        self.elements.change_plan_shipping_icon = '[class^="changePlanModalContent__shipping-info-icon"]'
        self.elements.print_less_message = '[class^="changePlanModalContent__footer-text"]'
        self.elements.additional_pages_tooltip = '[class^="changePlanModalContent__tooltip-container__"]'
        self.elements.additional_pages_tooltip_content = '[data-testid="tooltip-content"]'
        self.elements.upgrade_plan_title = '[data-testid="upgrade-plan-title"]'
        self.elements.upgrade_plan_subtitle = '[data-testid="upgrade-plan-subtitle"]'
        self.elements.current_bc_card = '[data-testid="upgrade-plan-current-bc-card"]'
        self.elements.current_bc_icon = '[data-testid="upgrade-plan-current-bc-card"] svg'
        self.elements.current_bc_radio = '[id="current-billing-cycle-radio"]'
        self.elements.next_bc_card = '[data-testid="upgrade-plan-next-bc-card"]'
        self.elements.next_bc_icon = '[data-testid="upgrade-plan-next-bc-card"] svg'
        self.elements.next_bc_radio = '[id="next-billing-cycle-radio"]'
        self.elements.back_button_choose_plan = '[type="button"]'
        self.elements.confirm_button_choose_plan = '[data-testid="upgrade-plan-confirm-button"]'
        self.elements.change_plan_10_button = '[data-testid="change-plan-10-pages"]'
        self.elements.change_plan_25_button = '[data-testid="change-plan-25-pages"]'
        self.elements.change_plan_50_button = '[data-testid="change-plan-50-pages"]'
        self.elements.change_plan_100_button = '[data-testid="change-plan-100-pages"]'
        self.elements.change_plan_300_button = '[data-testid="change-plan-300-pages"]'
        self.elements.change_plan_500_button = '[data-testid="change-plan-500-pages"]'
        self.elements.change_plan_700_button = '[data-testid="change-plan-700-pages"]'
        self.elements.dot_icon_ink = '[class^="changePlanCard__change-plan-card-bullet-ink"]'

    def select_ink_plan(self, plan_pages: str):
        plan_selector = f'[data-testid="change-plan-{plan_pages}-pages"]'
        self.page.locator(plan_selector).click()

    def back_button_choose_plan(self):
        return self.page.locator(self.elements.back_button_choose_plan, has_text="Back")
