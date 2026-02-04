from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class UpdatePlanPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Plan Details card
        self.elements.plan_details_card = "[data-testid='plan-details-container']"
        self.elements.replace_printer_link = "[data-testid='replace-printer-link']"
        self.elements.cancel_instant_ink = '[data-testid="plan-details-container"] [data-testid="cancel-your-plan"]'
        self.elements.cancel_paper_add_on = '[data-testid="open-paper-cancelation"]'
        self.elements.contact_support_link = "[data-testid='contact-hp-support']"
        self.elements.change_shipping_link = "[data-testid='change-shipping-info']"
        self.elements.change_billing_info_link = "[data-testid='change-billing-info']"
        self.elements.prepaid_code_link = "[data-testid='redeem-new-offer-button']"
        self.elements.free_trial_plan_details = "[data-testid='free-months-message']"
        self.elements.paper_free_months = "[data-testid='paper-trial-month-message']"
        self.elements.pause_plan_info = '[data-testid="paused-plan-information"]'
        self.elements.resume_plan_link = '[data-testid="resume-link"]'
        self.elements.special_offers_balance = "[data-testid='special-offer-info-text']"
        self.elements.plan_information = "[data-testid='plan-information']"
        # Plan Cards
        self.elements.plan_10 = "[data-testid='plans-selector-plan-card-container-0']"
        self.elements.plan_25 = "[data-testid='plans-selector-plan-card-container-1']"
        self.elements.plan_50 = "[data-testid='plans-selector-plan-card-container-2']"
        self.elements.plan_100 = "[data-testid='plans-selector-plan-card-container-3']"
        self.elements.plan_300 = "[data-testid='plans-selector-plan-card-container-4']"
        self.elements.plan_500 = "[data-testid='plans-selector-plan-card-container-5']"
        self.elements.plan_700 = "[data-testid='plans-selector-plan-card-container-6']"
        self.elements.plan_1500 = "[data-testid='plans-selector-plan-card-container-7']"
        # Downgrade Plan Modal
        self.elements.downgrade_plan_confirmation = '[data-testid="downgrade-plan-confirmation-modal"]'
        self.elements.cancel_change_plan_button = '[data-testid^="cancel-change-plan-button"]'
        self.elements.cancel_change_plan_link = '[data-testid="cancel-change-plan-link"]'
        self.elements.undo_plan_change_cancel_button = '[data-testid^="undo-plan-change-cancel-button"]'
        self.elements.undo_plan_change_confirmation = '[data-testid="undo-plan-change-modal"]'
        self.elements.change_plan_button = '[data-testid^="change-plan-button"]'
        self.elements.plan_downgrade_close_modal_button = '[data-testid="downgrade-plan-confirmation-modal"] [class^="vn-modal__close"]'
        # Upgrade Plan Modal
        self.elements.upgrade_plan_confirmation = '[data-testid="upgrade-plan-confirmation-modal"]'
        self.elements.upgrade_next_month = '[data-testid="upgrade-next"]'
        self.elements.upgrade_current_month = '[data-testid="upgrade-current"]'
        # Pause Plan
        self.elements.plan_100_resume_tag = '[data-testid="plans-selector-plan-card-3-plan-tag-container"]'
        self.elements.plan_100_resume_button = '[data-testid="plans-selector-resume-plan-button-3"]'
        # Header
        self.elements.header_cancel_link = "[data-testid='page-header-subtitle'] [data-testid='cancel-your-plan']"
        self.elements.header_remove_paper_link = "[data-testid='page-header-subtitle'] [data-testid='legal-remove-paper-link']"
        # Page elements
        self.elements.page_title = "[id='change-plan'] [data-testid='page-title']"
        self.elements.plan_card_container = "[class^='styles__PlanSelectorContainer']"
        self.elements.free_trial_info_card = "[class^='remainingTrialMonthsCard__content']"
        self.elements.disclaimer_card = "[class='disclaimer-container']"
        self.elements.print_history_link = "[class='disclaimer-container'] > p:nth-child(1) > a"
        self.elements.terms_and_service_link = "[class='disclaimer-container'] > p:nth-child(2) > a"
        self.elements.pending_change_plan = '[data-testid="pending-plan-banner"]'
        self.elements.change_plan_button_10 = '[data-testid="change-plan-button-10"]'
        self.elements.change_plan_button_25 = '[data-testid="change-plan-button-25"]'
        self.elements.change_plan_button_50 = '[data-testid="change-plan-button-50"]'
        self.elements.change_plan_button_100 = '[data-testid="change-plan-button-100"]'
        self.elements.change_plan_button_300 = '[data-testid="change-plan-button-300"]'
        self.elements.change_plan_button_500 = '[data-testid="change-plan-button-500"]'
        self.elements.change_plan_button_700 = '[data-testid="change-plan-button-700"]'
        self.elements.change_plan_button_1500 = '[data-testid="change-plan-button-1500"]'
        self.elements.dashboard_plan_selector_paper_card_button = '[data-testid="dashboard-plan-selector-paper-card-button"]'

    def get_select_plan_button(self, pages: int):
        plan_attr = f"change_plan_button_{pages}"
        if hasattr(self, plan_attr):
            return getattr(self, plan_attr)
        else:
            raise ValueError(f"Plan with {pages} pages not found in UpdatePlanPage.")

    def get_plan_by_position(self, plan_number: int):
        return self.page.locator(f"[data-testid='plans-selector-plan-card-container-{plan_number}']")

    def get_plan_by_pages(self, pages: int):
        plan_attr = f"plan_{pages}"
        if hasattr(self, plan_attr):
            return getattr(self, plan_attr)
        else:
            raise ValueError(f"Plan with {pages} pages not found in UpdatePlanPage.")

    @property
    def cancel_instant_ink(self):
        return self.page.locator(self.elements.cancel_instant_ink).last

    @property
    def free_trial_info_card(self):
        return self.page.locator(self.elements.free_trial_info_card).first
