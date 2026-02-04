from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class OverviewPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Enroll or Replace a Printer
        self.elements.enroll_or_replace_button = "[data-testid='enroll-printer-link']"
        self.elements.enroll_printer_button = "[data-testid='enroll-another-printer-v2-link']"
        self.elements.replace_printer_button = "[data-testid='simplified-replace-printer-link']"
        self.elements.finished_replacing_printer_modal = "[data-testid='acknowledge-modal-button']"
        self.elements.complete_enrollment_button = "[data-testid='complete-enrollment']"
        self.elements.connect_later_button = "[data-testid='connect-later-button']"
        self.elements.printer_replacement_page = '[class^="printerReplacementPage__printer-replacement-page-container"]'
        self.elements.enroll_modal_close = '[class^="vn-modal__close"]'
        # Status Card
        self.elements.status_card = "[data-testid='status-card']"
        self.elements.status_card_body = "[id^='defaultStatusCardBody__default-status-card-body']"
        self.elements.status_card_title = "[data-testid='status-card-title']"
        self.elements.status_card_cloud_kick = "[data-testid='cloud-kick-container']"
        self.elements.status_card_printer_name = "h2[data-testid='printer-name']"
        self.elements.printer_details_link = "[data-testid='printer-details-link']"
        self.elements.view_print_history_link = "[data-testid='view-print-history']"
        self.elements.monthly_summary = "[data-testid='monthly-summary']"
        self.elements.plan_pages_bar = "[data-testid='plan-pages-progress-bar']"
        self.elements.trial_pages_bar = "[data-testid='trial-pages-progress-bar']"
        self.elements.rollover_pages_bar = "[data-testid='rollover-pages-progress-bar']"
        self.elements.credited_pages_bar = '[data-testid="credit-progress-bar"]'
        self.elements.additional_pages_bar = '[data-testid="additional-progress-bar"]'
        self.elements.complimentary_pages_bar = '[data-testid="plan-progress-bar"]'
        self.elements.notification_status_card = "[data-testid='inline-notification']"
        self.elements.total_pages_printed = '[class^="monthlySummaryContent__pages-info-container"],[data-testid="total-pages-printed"]'
        self.elements.printer_status_tooltip = '[id^="printerStatusRow__printer-status-row"] [class^="printerStatus__printer-status"]'
        self.elements.estimated_charge = "[id='estimated-charge']"
        self.elements.date_range_container = '[class^="monthlySummaryContent__date-range-container"]'
        self.elements.set_pages_addicional = '[class^="progressBar__text-set-pages-additional"]'
        self.elements.enroll_printer_again_button = '[data-testid="re-enroll-button"]'
        self.elements.download_past_invoices = '[data-testid="view-print-history"]'
        self.elements.browse_plans_link = '[data-testid="plans-banner-browse-plans-link"]'
        self.elements.plan_suggestion_banner = '[data-testid="plan-suggestion-test"]'
        # Printer Info
        self.elements.printer_selector = "[data-testid='printer-selector']"
        self.elements.printer_selector_first_printer = '[class^="caption-small option__printer-serial-number"]'
        self.elements.printer_selector_printers = '[class^="selectablePrinters__selectable-printers-container-new"] [data-testid^="printer-option-"]'
        self.elements.printer_offline_message = '[class^="connectivityBanner__connectivity-banner"]'
        self.elements.connectivity_guide_link = '[class^="connectivityBanner__connectivity-banner"] [class^="connectivityBanner__banner-label"]'
        self.elements.printers_grouped_by_status = '[class^="selectablePrinters__selectable-printers-container-"]'
        self.elements.printer_selector_option = '[data-testid="selectable-printer"]'
        # Printer Details Modal
        self.elements.printer_details_modal = "[data-testid='printer-details-modal']"
        self.elements.printer_details_modal_title = "[data-testid='printer-details-modal'] h6"
        self.elements.printer_details_modal_printer_img = "[data-testid='printer-details-modal-printer-image']"
        self.elements.printer_details_modal_printer_info = "[data-testid='print-details-modal-printer-info']"
        self.elements.printer_details_modal_close_button = "[data-testid='printer-details-modal'] [class^='vn-modal__close']"
        self.elements.resume_button = '[data-testid="confirm-subscription-resume-modal-content-resume-button"]:visible'
        self.elements.back_button = '[data-testid="confirm-subscription-resume-modal-content-back-button"]:visible'
        # Ink Cartridge Status Card
        self.elements.cartridge_status_card = "[data-testid='ink-status-card']"
        self.elements.view_shipments_link = "[data-testid='view-shipments']"
        self.elements.recycle_your_cartridge_link = "[data-testid='recycle-link']"
        self.elements.cartridge_status_card_description = '[data-testid="subscribed-no-pens-description"]'
        # Plan Details Card
        self.elements.plan_details_card = "[data-testid='plan-details-column']"
        self.elements.subscription_id = '[id^="planDetailsColumn__plan-details-column_"] p[class="caption-small"]'
        #self.elements.subscription_id = '[data-testid="plan-details-column"] [class="caption-small"]'        
        self.elements.plan_information = "[data-testid='plan-information']"
        self.elements.free_months = '[data-testid="free-months-message"], [data-testid="free-months-message-parity"]'
        self.elements.paper_free_months = '[data-testid="paper-trial-month-message"]'
        self.elements.billing_section_plan_details = '[class^="billingSection__billing-section-payment-container"]'
        self.elements.change_billing_link = "[data-testid='change-billing-info']"
        self.elements.shipping_section_plan_details = '[class^="shippingSection__shipping-section"]'
        self.elements.change_shipping_link = "[data-testid='change-shipping-info']"
        self.elements.change_plan_link = "[data-testid='change-plan-link'] > span"
        self.elements.special_offers_balance = "[data-testid='special-offer-info-text']"
        self.elements.redeem_code_link = "[data-testid='redeem-new-offer-button']"
        self.elements.cancel_instant_ink = '[data-testid="cancel-your-plan"]'
        self.elements.transfer_subscription_link = '[data-testid="simplified-printer-replacement-button"]'
        self.elements.pause_plan_link = '[data-testid="pause-ii-plan-link-update-plan"], [data-testid="pause-your-plan"]'
        self.elements.pause_plan_info = '[data-testid="paused-plan-information"]'
        self.elements.add_payment_method_link = "[data-testid='change-billing-info']"
        self.elements.no_active_plans = '[data-testid="printer-no-active-plan"]'
        self.elements.keep_enrollment_button = '[data-testid="cancellation-banner"] button'
        self.elements.paypal_info = '[data-testid="pay_pal-payment-information"]'
        self.elements.message_add_billing_info = "[id='warning-secondary-text']"
        self.elements.alert_message = "[src='//assets-stage1.instantink.com/vulcan/icons/alert.dbd3e29e189a9a2f46a032287a587812.png']"
        self.elements.critical_message = "[src='//assets-stage1.instantink.com/vulcan/icons/critical.0e32c252780938f750686f597a1906b6.png']"
        self.elements.savings_calculator_card = "[data-testid='savings-calculator']"
        self.elements.savings_calculator_card_annual_savings = "[class^='savingsCalculatorCard__savings-text']"
        self.elements.savings_calculator_tooltip_icon = "[class^='savingsCalculatorCard__icon-tooltip_']"
        self.elements.savings_calculator_tooltip_printing_average = "[data-testid='savings-calculator-toolkit'] p:nth-child(1)"
        self.elements.savings_calculator_tooltip_traditional_cartridge_cost = "[data-testid='savings-calculator-toolkit'] p:nth-child(2)"
        self.elements.keep_enrollment_confirmation = "[data-testid='confirm-subscription-resume-modal-content-resume-button']"
        # Promo Code Modal
        self.elements.modal_offers = "[data-testid='prepaid-modal']"
        self.elements.promo_code_input_box = "[data-testid='promo-code-input-box']"
        self.elements.accept_promo_code_checkbox = "[class^='promoModal__promo-code-checkbox']"
        self.elements.apply_promo_code_button = "[data-testid='apply-promo-code-button']"
        self.elements.promo_code_success_message = '[id="benefit-amount"]'
        self.elements.promo_code_helper_text = '#promo-code-text-box-helper-text'
        self.elements.close_promo_code_modal = '[data-testid="cancel-promo-code-button"]'
        # Special Offers Card
        self.elements.raf_card = "[data-testid='refer-a-friend-promo-content']"
        self.elements.special_offer_card = '[data-testid="promo-card"]'
        self.elements.raf_code = '[class^="referAFriendPromoContentNewVisId__share-url"]'
        # First Access Elements
        self.elements.continue_setting_preferences = "[data-testid='user-preference-continue-btn']"
        self.elements.accept_all_preferences = "[id='consent-accept-all-button']"
        self.elements.skip_tour = '[data-testid="skip-tour-button"]'
        self.elements.no_paper_offer_modal = "[data-testid='paper-new-plan-offer-main-div'] [data-testid='not-now-button']"
        self.elements.start_tour = '[data-testid="start-tour-button"]'
        self.elements.special_savings_modal_close = "[data-testid='special-savings-modal'] button"
        # Connected printing services
        self.elements.manage_options_button = '[data-testid="redirect-btn"]'
        self.elements.decline_button = '#consent-decline-all-button'
        # Privacy consents
        self.elements.privacy_consents_items = '[data-testid="user-tour-modal"] label:has(input)'
        self.elements.set_personalized_suggestions_button = '[data-testid="setPersonalizedSuggestions-btn"]'
        self.elements.set_advertising_button = '[data-testid="setAdvertising-btn"]'
        self.elements.set_analytics_button = '[data-testid="setAnalytics-btn"]'
        self.elements.consent_back_button = '#consent-back-button'
        self.elements.consent_continue_button = '#consent-continue-button'
        # Privacy card
        self.elements.privacy_card = '[class^="privacyCard__content-wrapper"]'
        self.elements.share_usage_data_link = '[data-testid="share-usage-data"]'
        # Ink Cartridge
        self.elements.cmyCartridgeItem = "[data-testid='cmy-item-container']"
        self.elements.kCartridgeItem = "[data-testid='k-item-container']"
        self.elements.cCartridgeItem = "[data-testid='c-item-container']"
        self.elements.mCartridgeItem = "[data-testid='m-item-container']"
        self.elements.yCartridgeItem = "[data-testid='y-item-container']"
        self.elements.no_pens_status = "[class^='subscribedNoPensInkStatusBody__subscribed-no-pens-description']"
        # Pause Plan
        self.elements.pause_plan_modal = "#pause-plan-modal-container, [data-testid='pause-plan-modal']"
        self.elements.pause_plan_dropdown = '[datetest-id="pause-plan-months-select"]'
        self.elements.confirm_pause_plan = '[data-testid="pause-plan"]'
        self.elements.plan_paused_banner = '[data-testid="pause-plan-banner"]'
        self.elements.resume_plan_link = '[data-testid="resume-plan-pause-link"]'
        self.elements.confirm_resume_plan_modal = '[data-testid="banner-plan-resume-modal"]'
        self.elements.keep_paused_button = '[data-testid="keep-paused-button-modal"]'
        self.elements.resume_plan_button = '[data-testid="resume-plan-button-modal"]'
        self.elements.plan_100_resume_text = '[data-testid="paused-plan-info"]'
        # Tour elements
        self.elements.next_button_update_your_plan_tooltip = '[data-testid="next-0"]'
        self.elements.next_button_billing_shipping_tooltip = '[data-testid="next-1"]'
        self.elements.last_button_raf_tooltip = '[data-testid="last-2"]'
        self.elements.tour_tooltip_close_button = '[class^="tourTooltip__close-button"]'
        # Alert messages
        self.elements.suspended_text = '#suspended'
        # Footer elements
        self.elements.footer = '[data-testid="consumer-footer"] a'
        self.elements.footer_hp_com = '[data-testid="footer-hp-com"]'
        self.elements.footer_wireless_print_center = '[data-testid="footer-wireless-print-center"]'
        self.elements.footer_help_center = '[data-testid="footer-help-center"]'
        self.elements.footer_terms_of_use = '[data-testid="footer-terms-of-use"]'
        self.elements.footer_hp_privacy = '[data-testid="footer-hp-privacy"]'
        self.elements.footer_hp_your_privacy_choices = '[data-testid="footer-hp-your-privacy-choices"]'
        # Unsubscribed status card       
        self.elements.unsubscribed_enroll_printer_again_button = '[data-testid="unsubscribed-status-card-content-consumer-enroll-again-anchor-button"]'
        self.elements.unsubscribed_hp_shop_ink_button = '[data-testid="unsubscribed-status-card-content-hp-shop-anchor-button"]'
        self.elements.unsubscribed_download_past_invoices = '[data-testid="unsubscribed-status-card-content-download-past-invoices"], [data-testid="view-print-history"]'
        # Support Card
        self.elements.support_card = '[class^="supportCard__support-container"]'
        self.elements.support_card_icon = '[class^="supportCard__support-container"] svg'
        self.elements.support_card_title = '[class^="supportCard__support-container"] h6[class^="supportCard__title_"]'
        self.elements.support_card_description = '[class^="supportCard__support-container"] p[class^="supportCard__description"]'
        self.elements.support_card_link = '[data-testid="support-card-link"]'
        # PaaS Banner
        self.elements.paas_banner = '[class^="paasOfferCard__paas-offer-card-container_"]'
        self.elements.paas_image = '[class^="paasOfferCard__paas-offer-card-image_"]'
        self.elements.pass_title = '[class^="paasOfferCard__paas-offer-card-title_"]'
        self.elements.pass_description = '[class^="paasOfferCard__paas-offer-card-description_"]'
        self.elements.pass_link = '[class^="paasOfferCard__paas-offer-card-link_"]'
        # Emergency Banner
        self.elements.orange_banner = '[class^="colorOrange"]'
        self.elements.red_banner = '[class^="colorRed"]'
        self.elements.blue_banner = '[class^="colorBlue"]'
        self.elements.banner_header = '[data-testid="banner-heading"]'
        self.elements.banner_content = '[data-testid="banner-content"]'
        self.elements.banner_arrow = '[data-testid="emergency_banner_collapse_expand"]'
        self.elements.banner_dismiss = '[data-testid="emergency_banner_dismiss"]'
        # Paper Subscription Elements
        self.elements.paper_status = '[class^="styles__PaperStatusContainer"]'
        self.elements.status_card_paper = '[data-testid="monthly-paper-summary-enrolled-container"]'
        self.elements.paper_monthly_summary = '[data-testid="paper-summary-title"]'
        self.elements.paper_billing_cycle = '[data-testid="monthly-paper-summary-billing-cycle-interval"]'
        self.elements.paper_estimated_charge = '[data-testid="monthly-paper-summary-pricing-tax"]'
        self.elements.paper_sheets_used = '[data-testid="monthly-paper-summary-sheets-used-amount"]'
        self.elements.paper_plan_pages_bar = "[data-testid='monthly-paper-summary-enrolled-container'] [data-testid='plan-progress-bar']"
        self.elements.paper_trial_pages_bar = "[data-testid='monthly-paper-summary-enrolled-container'] [data-testid='trial-progress-bar']"
        self.elements.paper_rollover_pages_bar = "[data-testid='monthly-paper-summary-enrolled-container'] [data-testid='rollover-progress-bar']"
        self.elements.paper_no_pens_message = '[data-testid="paper-monthly-message"]'
        self.elements.paper_redeemed_message = '[data-testid="trial-state-container"]'
        self.elements.cancel_paper_add_on = '[data-testid="legal-remove-paper-link"]'
        self.elements.paper_last_shipment = '[data-testid="shipment-date-id"]'
        self.elements.paper_cancellation_in_progress = '[data-testid="keep-paper-delivery-container-title"]'
        self.elements.keep_paper_button = '[data-testid="keep-paper-delivery-button"]'
        # Ink page
        self.elements.page_title = "#rebranded-home-page"
        self.elements.close_finish_enrollment_button = '[class*="acknowledgeModal__ack-modal-content___"]'
        #self.elements.close_finish_enrollment_button = '[data-testid="acknowledge-modal-button"]'
        self.elements.restore_subscription = '[data-testid="restore_subscription"]'
        self.elements.resume_instant_ink_subscription = '[data-testid="resume-instant-ink-subscription"]'
        self.elements.overview_page_title = '[data-testid="page-title"]'
        self.elements.ink_cartridge_status_card = '[data-testid="line-notification-title"]'
        self.elements.confirm_resume_back_button = '[data-testid="back-to-cancel-confirmation"]'
        self.elements.close_timeline_modal = '[data-testid="close-timeline-modal"]'
        self.elements.cancellation_timeline_modal = '[data-testid="cancellation-timeline-modal"]'
        self.elements.subscription_resumed_banner = '[data-testid="subscription-resumed-banner"]'
        self.elements.close_pause_plan_button = '[data-testid="close-pause-plan-button"]'
        self.elements.pause_plan_info = '[data-testid="paused-plan-banner-title"]'
        self.elements.credit_card_payment_info = '[data-testid$="-payment-information"]'
        self.elements.credit_card_expiration_info = '[data-testid="billing-section-credit-card-expiration-info"]'
        self.elements.shipping_information = '[data-testid="shipping-information"]'
        self.elements.shipping_address_street = '[data-testid="street-name"]'
        self.elements.shipping_address_city_state_zip = '[data-testid="shipping-information"] > div > p:nth-child(2)' 
        self.elements.printer_selector = '[data-testid="printer-selector"]'
        self.elements.avatar_menu = '[data-testid="jarvis-react-consumer-layout__avatar_menu"]'
        self.elements.sign_out_button = '[data-testid="jarvis-react-consumer-layout__logout_button"]'
        self.elements.billing_issues_banner = '[data-testid="billing-issues-banner"]'
        self.elements.expired_session_login = '[data-testid="critical-scopes-modal"] [class^="buttonsContainer"] button:nth-child(2), [data-testid="modalLoginButton"]'
        self.elements.expired_session_cancel = '[data-testid="critical-scopes-modal"] [class^="buttonsContainer"] button:nth-child(1),[data-testid="modalCloseButton"]'
        self.elements.update_payment_method = '[data-testid="payment-suspended-banner"] button'

        # Flip elements
        self.elements.enter_address = "[data-testid='enter-address']"
        self.elements.enroll_now = "[data-testid='enroll-now']"
        self.elements.flip_modal_enter_address_button = "[data-testid='flip_modal_enter_address_button']"
        self.elements.flip_modal_not_now_button = "[data-testid='flip_modal_not_now_button'], [data-testid='flip_modal_close_button']"
        
		# Paper 
        self.elements.paper_modal_claim_button = "[data-testid='instant-paper-modal-claim-button']"
        self.elements.paper_hero_banner_button = "[data-testid='instant-paper-hero-banner-button']"
        self.elements.paper_pre_enroll_content_continue_button = "[data-testid='instant-paper-pre-enroll-content-continue-button']"
        self.elements.paper_plan_review_confirm_button = "[data-testid='instant-paper-plan-review-confirm-button']"
        self.elements.paper_checkbox_redeem = "[data-testid='checkbox-redeem']"
        self.elements.paper_redeem_button = "[data-testid='redeem-paper-button']"
        self.elements.paper_remove_link = "[data-testid='legal-remove-paper-link']"
        self.elements.confirm_cancellation_button = "[data-testid='confirm-cancellation-button']"
        self.elements.keep_subscription_button = "[data-testid='keep-subscription-button']"

    def get_page_title(self, wait=60000):
        return self.page.wait_for_selector(self.elements.page_title, timeout=wait)

    def get_change_plan_link(self):
        return self.page.get_by_test_id(self.elements.change_plan_link).first

    def get_status_card_printer_name(self):
        return self.page.get_by_test_id(self.elements.status_card_printer_name).first
    
    @property
    def raf_code(self):
        return self.page.locator(self.elements.raf_code).last
