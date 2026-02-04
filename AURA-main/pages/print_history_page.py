from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class PrintHistoryPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Page elements
        self.elements.page_title = "[data-testid='page-title']"
        self.elements.print_history_card = "[data-testid='print-history-card-parity']"
        self.elements.print_history_card_title = "[data-testid='print-history-card-parity'] h6"
        self.elements.how_is_calculated_link = "[data-testid='how-is-billing-calculated-link']"
        self.elements.total_printed_pages = "[data-testid='total-pages-printed']"
        self.elements.free_months = '[data-testid="free-months-message"]'
        self.elements.print_history_section = '[data-testid="print-history-section"]'
        self.elements.plan_details_card = '[data-testid="billing-summary"]'
        self.elements.account_suspended_banner = '[data-testid="payment-suspended-banner"]'

        # Progress bars
        self.elements.plan_pages_bar = "[data-testid='plan-progress-bar']"
        self.elements.trial_pages_bar = "[data-testid='trial-progress-bar']"
        self.elements.rollover_pages_bar = "[data-testid='rollover-progress-bar']"
        self.elements.additional_pages_message = '[class^="progressBar__text-set-pages-additional"]'
        
        # Cards
        self.elements.plan_details_card = "[class^='printHistory__columnB'] [data-testid='billing-summary']"
        self.elements.faq_card = "[data-testid='print-history-jarvis-faq']"
        
        # FAQ questions
        self.elements.faq_question_1 = "[aria-controls='item-0']"
        self.elements.faq_question_2 = "[aria-controls='item-1']"
        self.elements.faq_question_3 = "[aria-controls='item-2']"
        self.elements.faq_question_4 = "[aria-controls='item-3']"
        
        # FAQ answers
        self.elements.faq_answer_1 = "#item-0"
        self.elements.faq_answer_2 = "#item-1"
        self.elements.faq_answer_3 = "#item-2"
        self.elements.faq_answer_4 = "#item-3"
        
        # FAQ links
        self.elements.print_faq = '[data-testid="accordion"] > div'
        self.elements.faq_terms_of_service_link = "[data-testid='print-history-faq-2-terms-of-service-link']"
        self.elements.faq_overview_link = "[data-testid='print-history-faq-2-plan-overview-link']"
        self.elements.update_plan_link = "[data-testid='print-history-faq-2-change-plan-link']"
        self.elements.faq_terms_of_service_link = "[data-testid='print-history-faq-2-terms-of-service-link']"
        self.elements.print_history_submenu = "[data-testid='print-history-submenu']"

        # Table elements
        self.elements.print_history_table_button = '[data-testid="history-table-container"] h3>button'
        self.elements.print_history_table = '[data-testid="history-table-container"] table'
        self.elements.table_date = "#date button"
        self.elements.table_description = "#description"
        self.elements.table_invoice = "#urlText"
        self.elements.table_selector = "[class^='historyTable__selector']"
        self.elements.table_selector_list = "[data-testid='history-table-select-options']"
        self.elements.billing_cycle_option = '[data-testid="print-history-chart-parity"] [class^="vn-select__buttons"]'
        self.elements.billing_cycle_options = '#vn-select-1-listbox > li, [id$="listbox"] > li'
        self.elements.select_1_option = '[id$="-option-1"]'
        self.elements.select_2_option = '[id$="-option-2"]'
        self.elements.select_3_option = '[id$="-option-3"]'
        self.elements.billing_cycle_period_title = "[data-testid='select-billing-cycle-parity'] input"
        self.elements.total_pages_printed = '[data-testid="total-pages-printed"]'
        self.elements.plan_pages_text = '[data-testid="plan-pages-progress-bar"] [data-testid^="text-values-"]'
        self.elements.rollover_pages_text = '[data-testid="text-values-rollover"]'
        self.elements.additional_pages_text = '[data-testid="text-values-additional"]'
        self.elements.plan_price_text = '[data-testid="plan-description"]'
        self.elements.overage_description_text = '[data-testid="overage-description"]'
        self.elements.previous_billing_text = '[data-testid="previous-overage-amount"]'
        self.elements.current_billing_text = '[data-testid="pre-tax-amount"]'
        self.elements.current_total_text = '[data-testid="total-amount"]'
        self.elements.download_all_invoices_button = '[data-testid="all-invoices-download-button"]'
        self.elements.payment_problem_banner = '[data-testid="payment-problem-banner"]'
        self.elements.print_history_table_description = "[class*='activity-description']"
        self.elements.paper_summary = '[data-testid="paper-addon-summary-wrapper"]'

    @property
    def faq_update_plan_link(self):      
        return self.page.locator(self.elements.faq_update_plan_link).first
    
    @property
    def plan_price_text(self):      
        return self.page.locator(self.elements.plan_price_text).first
