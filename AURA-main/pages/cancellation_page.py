from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class CancellationPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Printer Information
        self.elements.printer_img = 'xpath=(//*[@data-testid="printer-img"])[2]'
        self.elements.printer_info_name = 'xpath=(//*[@data-testid="printer-info-name"])[2]'
        self.elements.printer_info_serial = '[data-testid="printer-info-serial"]'
        # Cancellation Summary Elements
        self.elements.cancellation_summary_image = '[class^="cancellationSummaryCard__animation-container___2zlva"]'
        self.elements.subscribed_info = '[data-testid="cancellation-summary-information"]'
        self.elements.confirm_cancellation_button = "[data-testid='confirm-cancellation'],[data-testid='confirm-cancellation-button']"
        self.elements.keep_enrollment_button = "[data-testid='keep-subscription-button']"
        self.elements.bottom_section_title = '[data-testid="cancellation-retention-new-layout-title"]'
        #self.elements.change_plan_link = '[data-testid="change-to-a-different-plan"]'
        self.elements.change_plan_link = 'xpath=//*[text()="Change your plan"]'
        self.elements.pause_plan_link = '[data-testid="pause-your-plan"], [data-testid="cancellation-alternative-pause-your-plan"]'
        self.elements.transfer_subscription_link = 'xpath=//*[text()="Transfer your subscription"]'
        self.elements.contact_hp_support_link = '[data-testid="contact-hp-support"]'
        self.elements.only_pay_when_you_need_to_print_link = '[data-testid="switch-to-pay-as-you-print-open"]'
        self.elements.pause_plan_modal = '[data-testid="pause-plan-modal"]'
        # Change Plan Modal
        self.elements.change_plan_modal = '[class^="changePlanModalContent__change-plan-container"]'
        self.elements.plan_10_button = '[data-testid="change-plan-10-pages"]'
        self.elements.plan_25_button = '[data-testid="change-plan-25-pages"]'
        self.elements.plan_50_button = '[data-testid="change-plan-50-pages"]'
        self.elements.plan_100_button = '[data-testid="change-plan-100-pages"]'
        self.elements.plan_300_button = '[data-testid="change-plan-300-pages"]'
        self.elements.plan_500_button = '[data-testid="change-plan-500-pages"]'
        self.elements.plan_700_button = '[data-testid="change-plan-700-pages"]'
        self.elements.plan_1500_button = '[data-testid="change-plan-1500-pages"]'
        self.elements.additional_pages_tooltip = '[class^="changePlanModalContent__tooltip-container__"]'
        self.elements.additional_pages_tooltip_content = '[data-testid="tooltip-content"]'
        # Other Page Elements
        self.elements.continue_button = '[data-testid="continue-to-cit-survey"], [data-testid="continue-to-paper-cit-survey"]'
        self.elements.return_to_account_button ='[data-testid="return-to-account-button"]'
        self.elements.submit_feedback_button = '[data-testid="submit-feedback-button"]'
        self.elements.do_not_print_enough_radio = '[data-testid="i-do-not-print-enough-to-make-it-worthwhile"]'
        self.elements.service_is_too_expensive_radio = '[data-testid="the-service-is-too-expensive"]'
        self.elements.did_not_received_my_shipment_radio = '[data-testid="did-not-receive-shipment-or-problem-cartridge"]'
        self.elements.have_replaced_my_printer_radio = '[data-testid="replaced-or-plan-to-replace-printer"]'
        self.elements.wifi_issues_with_my_printer_radio = '[data-testid="technical-or-wifi-issue-w-printer"]'
        self.elements.other_option_radio = '[data-testid="other"]'
        self.elements.feedback_text_box = '[id="feedback-reason"]'
        self.elements.cancellation_in_progress = '[class^="warnings__warning-text"]'
        self.elements.keep_subscription_button = '[data-testid="keep-subscription-button"]'
        self.elements.restore_subscription_button = '[data-testid="restore_subscription"]'
        self.elements.whats_happens_next = '[data-testid="timeline-header-info"]'
        self.elements.close_modal_button = "[class^='vn-modal__close']"
        self.elements.cancellation_card = '[data-testid="optimized-cancellation-summary-card"]'
        self.elements.cancellation_animation = '[class^="cancellationLoading__cancellation-loading-animation-container_"],div[class*="cancellationSummaryCard__animation-container"]'
        # Cancellation Feedback Page
        self.elements.cancellation_feedback_title = '[data-testid="cancellation-feedback-title"]'
        self.elements.cancellation_feedback_subtitle = '[data-testid="cancellation-feedback-subtitle"]'
        self.elements.feedback_img = '[class^="cancellationFeedback__feedback-header-animation-container"]'
        self.elements.cancellation_title='xpath=//*[text()="Cancel Plan"]'
        self.elements.below_subscription_info='[class="cancellationSummaryContent__description-body___1A-tG"]'
        self.elements.last_day_billing_cycle_text='xpath=(.//*[contains(@class, "cancellationSummaryContent")]//p)[3]'
        self.elements.printer_replacement_title='xpath=//*[text()="Which printer are you enrolling as your replacement?"]'
        self.elements.contact_support_link='xpath=//*[text()="Contact our expert support"]'
        self.elements.contact_us_tab='xpath=//*[text()=" Contact Us "]'
        self.elements.support_page_header='xpath=//*[text()="How would you like to connect with us?"]'
        self.elements.close_popup='[aria-label="close"]'
        self.elements.popup_frame='[class="modal-content"]'
        self.elements.section1_timeline='[class="cancellationTimelineContent__timeline-content-header-wrapper___13VFp"],[class="cancellationSuccessTimeline__trade-price-card___1B_bi"]'
        self.elements.section2_timeline='[class="timelineStepper__timeline-stepper-container___35SjP"],[class="timelineStepper__timeline-stepper-container___1LTza"]'
        self.elements.section3_timeline='[class="cancellationRetention__cancellation-retention-container___ewj0f"],[class="optimizedCancellationRetention__optimized-cancellation-retention-container___3ut82"]'
        self.elements.confirm_subscription_resume_modal='[data-testid="confirm-subscription-resume-title"]'
        self.elements.radio_button='[class="vn-radio-button__icon css-1qduhqr"]'
        self.elements.cancellation_loading_page_title='xpath=//*[text()="Just a second, your cancellation is being processed..."]'
        self.elements.summary_page_back_button='xpath=//*[text()="Back"]'
        # Paper Elements
        self.elements.confirm_paper_cancellation_button = '[data-testid="confirm-paper-cancellation"], [data-testid="confirm-cancellation-button"]'
        self.elements.keep_paper_button = '[data-testid="keep-paper-subscription"], [data-testid="keep-subscription-button"]'
        # Paper Cancellation Feedback Radio Buttons
        self.elements.replenishment_anxiety_radio = '[data-testid="replenishment-anxiety"]'
        self.elements.leakage_radio = '[data-testid="leakage"]'
        self.elements.did_not_print_enough_radio = '[data-testid="did-not-print-enough"]'
        self.elements.ran_out_of_paper_radio = '[data-testid="ran-out-of-paper"]'
        self.elements.paper_overages_radio = '[data-testid="paper-overages"]'
        self.elements.temporary_cancellation_radio = '[data-testid="temporary-cancellation"]'
        self.elements.stockpiling_radio = '[data-testid="stockpiling"]'
        self.elements.too_expensive_radio = '[data-testid="too-expensive"]'
        self.elements.damaged_paper_radio = '[data-testid="damaged-paper"]'
        self.elements.i_did_not_receive_shipment_radio = '[data-testid="i-did-not-receive-shipment"]'
        self.elements.moved_to_non_paper_service_area_radio = '[data-testid="moved-to-non-paper-service-area"]'
        self.elements.paper_quality_radio = '[data-testid="paper-quality"]'

    def get_plan_button(self, plan_pages: str):
        plan_attr = f"plan_{plan_pages}_button"
        if hasattr(self.elements, plan_attr):
            selector = getattr(self.elements, plan_attr)
            return self.page.locator(selector)
        else:
            raise ValueError(f"Plan button for {plan_pages} not found in CancellationPage.")
        