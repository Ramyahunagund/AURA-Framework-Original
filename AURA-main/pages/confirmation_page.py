from playwright.sync_api import Page
from pages.base_page_object import BasePageObject
import re

class ConfirmationPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Plan selection elements
        self.elements.monthly_plan = "[data-testid='i_ink-plan-type-card-select-button']"
        self.elements.ink_cartridges_tab = "[data-testid='ink-only-image-tab']"
        self.elements.paper_cartridges_tab = "[data-testid='ink-paper-image-tab']"
        self.elements.select_plan_button = "[data-testid='consumer-plans-select-plans']"
        self.elements.v3_content_area = '[data-testid="v3-content-area"]'
        self.elements.click_learn_more = 'text=Learn more'
        self.elements.how_it_works = 'text=How it works'
        self.elements.close_x_button = '[aria-label="Close modal"]'
        self.elements.blue_inf_icon = '[data-testid="plan-card-tooltip"]'
        self.elements.current_monthly_plan = '//div[@class="label css-iv5ce9" and @tabindex="0"]'
        self.elements.current_monthly_charges = '//*[text()="Ink + paper plan"]/preceding::div[@class="styles__PlanPriceContainer-@jarvis/react-instant-ink-plans__sc-r333w4-1 bxcBWX"]/h1'
        self.elements.review_trial_period = 'text=This is your plan when your trial ends on'
        self.elements.review_monthly_plan = '//h6[@class="styles__Frequency-@jarvis/react-smb-instant-ink-signup__sc-1hs3r93-12 iiPtQq"]'
        self.elements.review_monthly_pages = '//p[@class="styles__PagesPerMonth-@jarvis/react-smb-instant-ink-signup__sc-1hs3r93-15 byqQfq"]'
        self.elements.review_monthly_charges = '//p[@class="styles__PricePerMonth-@jarvis/react-smb-instant-ink-signup__sc-1hs3r93-16 jvaxLt"]'
        self.elements.review_trial_period = '//*[text()="This is your plan when your trial ends on"]'
        self.elements.confirmation_page = '//*[text()="Confirm your details to receive ink"]'
        self.elements.plan_card_title = '//*[text()="Your Plan"]'
        self.elements.plan_card_black_tick = '//*[@data-testid="plan-card"]/div/*[@fill="currentColor"]'
        self.elements.auto_printer_update = '[data-testid="auto-printer-page"]'
        self.elements.auto_printer_continue = '[data-testid="btn-continue"]'

        self.elements.plan_more_info = "[data-testid='plans-selector-plan-cards-more-info']"
        self.elements.plan_back_button = "[data-testid='learn-more-ink-back-button']"
        self.elements.learn_more_faq_modal = "[data-testid='learn-more-faq-modal']"
        self.elements.learn_more_faq_back_button = "[data-testid='learn-more-faq-back-button']"
        self.elements.plan_tooltip_icon = '[data-testid="plan-card-tooltip"]'
        self.elements.billing_tooltip_icon = '[data-analyticsid="billing-card-tooltip"]'
       # Plan card elements
        self.elements.plan_card = '[data-testid="plan-card"]'
        self.elements.plan_card_title = '[data-testid="plan-card"] [class^="styles__Title"]'
        self.elements.plan_box_footer = '[data-testid="planbox-footer"]'
        # Shipping elements
        self.elements.shipping_card = '[data-testid="shipping-card"]'
        self.elements.shipping_card_title = '[data-testid="shipping-card"] [class^="styles__Title"]'
        self.elements.shipping_card_description = '[data-testid="shipping-card"] [class^="styles__Description"]'
        self.elements.shipping_address_details = '[data-testid="shipping-card"] [class^="styles__Content"]'
        self.elements.add_shipping_button = "[data-testid='add-shipping'],[data-testid='edit-shipping']"
        self.elements.first_name = 'input[name="firstName"]'
        self.elements.last_name = 'input[name="lastName"]'
        self.elements.company_name_input = '[data-testid="company"]'
        self.elements.phone_number_input = "[data-testid='phoneNumberSmall']"
        self.elements.street1_input = "[data-testid='street1'], #street1"
        self.elements.street2_input = "[data-testid='street2'], #street2"
        self.elements.city_input = "[data-testid='city'], #city"
        self.elements.state_dropdown = "#state"
        #self.elements.state_text = "div[aria-controls='state-listbox'] > span"
        self.elements.zip_code_input = "[data-testid='zip-code'], #zip"
        self.elements.country = '[data-testid="country"]'
        self.elements.checkbox_text_message = '[data-testid="text-message-opt-in"]'
        self.elements.cancel_button = '[data-testid="cancel-button"]'
        self.elements.save_button = "[data-testid='save-button']"
        self.elements.suggested_address_modal = "div[data-testid='suggested-address-modal']"
        self.elements.suggested_address_option = "#suggested-address"
        self.elements.original_address_option = "#original-address"
        self.elements.ship_to_address_button = "[data-testid='ship-to-address-button']"
        self.elements.ship_to_address_button = "[data-testid='ship-to-address-button']"
        self.elements.error_message = '[class^="styles__ErrorMessage"]'
        self.elements.close_shipping_modal_button = '[data-testid="shipping-modal"] [aria-label="Close modal"]'
        self.elements.receive_update_msg = "text=Add your mobile phone to receive updates about your shipments and subscription status."
        self.elements.receive_update_checkbox = "[data-testid='text-message-opt-in'] input[type='checkbox']"
        self.elements.receive_update_checkbox = "[data-testid='text-message-opt-in'] input[type='checkbox'], [data-testid='text-message-opt-in']"
        self.elements.receive_update_checkbox_text = "text=I'd like to sign up for text messages to receive updates on my HP Instant Ink account."
        self.elements.blacklist_zipcode_error_text = "text=We’re sorry for the inconvenience"
        self.elements.blacklist_zipcode_back_button = "[data-testid='unsupported-postal-code-modal-go-back-button']"
        self.elements.error_message_no_longer_eligible = '[data-testid="error-msg"]'
        self.elements.shipping_card_black_tick = '//*[@data-testid="shipping-card"]/div/*[@fill="currentColor"]'

        self.elements.shipping_form_container = '[data-testid="shipping-form-container"]'
        # Billing PGS elements
        self.elements.billing_modal = "[class^='vn-modal--content']"
        self.elements.credit_card_radio_option = "[data-testid='credit-card-payment-box'] label"
        self.elements.use_shipping_address = "[data-testid='use-shipping-address'] input[type='checkbox']"
        self.elements.add_billing_button = "[data-testid='add-billing'], [data-testid='edit-billing']"
        self.elements.billing_information = "[data-testid='billing-card'] div p"
        self.elements.billing_company_input = '[data-testid="company-name"]'
        self.elements.tax_id_input = "#tax-id"
        self.elements.tax_id_tooltip = '[class="vn-input__icon"]'
        self.elements.tax_id_tooltip_msg = '[role=tooltip]'
        self.elements.billing_continue_button = "[data-testid='continue-button']"
        self.elements.iframe_pgs = "#pgs-iframe"
        self.elements.card_number = "#txtCardNumber"
        self.elements.exp_month = "#drpExpMonth"
        self.elements.exp_year = "#drpExpYear"
        self.elements.cvv_input = "#txtCVV"
        self.elements.billing_next_button = "#btn_pgs_card_add"
        self.elements.sca_save_button = "#btn_pgs_3dcard_add"
        self.elements.iframe_2fa = "#challengeFrame"
        self.elements.authentication_result_2fa = "#selectAuthResult"
        self.elements.acs_submit = "#acssubmit"
        self.elements.edit_billing_button = "[data-testid='edit-billing'], [class^='styles__ManagePaymentText-@monetization/shipping-billing-management']"
        self.elements.consumer_radio_button = '[data-testid="consumer-radio-button"]'
        self.elements.business_radio_button = '[data-testid="business-radio-button"]'
        self.elements.creditcard_radio_button = '[data-testid="credit-card-radio-button"]'
        self.elements.same_as_shipping_checkbox = '[data-testid="use-shipping-address"]'
        self.elements.street_name1_billing = "input[name='street1']"
        self.elements.street_name2_billing = "input[name='street2']"
        self.elements.city_billing = "input[name='city']"
        self.elements.state_billing = "div[id='state']"
        self.elements.zip_code_billing = "input[name='zip']"
        self.elements.card_number_input = "input[id='txtCardNumber']"
        self.elements.card_exp_month_input = "select[name='expMonth']"
        self.elements.card_exp_year_input = "select[name='expYear']"
        self.elements.card_cvv_input = "input[id='txtCVV']"
        self.elements.enter_cvv_error = 'text=" Please review and update your billing information"'
        self.elements.enter_mandatory_error = 'text="class=" (Your Complete Card Number, Expiration Month, Expiration Year, CVV Number)"'
        self.elements.pgs_card_continue = 'button[id="btn_pgs_card_add"]'

        self.elements.close_billing_button = "[data-testid='billing-modal'] [class^='vn-modal__close']"
        self.elements.back_button = "[data-testid='previous-screen-button']"
        self.elements.billing_card_info = "[data-analyticsid='billing-card-tooltip']"
        self.elements.btn_pgs_card_cancel = "#btn_pgs_card_cancel"
        # Billing 2CO elements
        self.elements.iframe_2co = "#cart-iframe"
        self.elements.continue_to_billing = "button.continue-to-billing"
        self.elements.continue_to_payment = "button.continue-to-payment"
        self.elements.card_name_2co = "input[name='name']"
        self.elements.first_name_2co = "input[name='firstName']"
        self.elements.last_name_2co = "input[name='lastName']"
        self.elements.card_number_2co = "input[name='card']"
        self.elements.exp_date_2co = "input[name='date']"
        self.elements.cvv_2co = "input[name='cvv']"
        self.elements.place_order_button = "button.place-order"

        # Billing PayPal elements
        self.elements.paypal_button = '[data-testid="paypal-button"]'
        self.elements.paypal_email_input = "#login_email, #email"
        self.elements.paypal_next_button = '[data-atomic-wait-intent="Submit_Email"], #btnNext'
        self.elements.paypal_password_input = "#password"
        self.elements.paypal_login_button = '[data-atomic-wait-intent="Submit_Password"], #btnLogin'
        self.elements.paypal_agree_button = "#consentButton"
        self.elements.paypal_link = '[data-testid="pay-pal-link"]'
        self.elements.paypal_method_btn = '[data-funding-source="paypal"]'
        self.elements.paypal_hpsmart_return = '[data-testid="return-to-hp-app-button"]'
        self.elements.paypal_status_check = "button:has-text('Check Status')"
        self.elements.paypal_link_done_btn = "button:has-text('Done')"


        # Billing Google Pay elements
        self.elements.google_pay_button = '[data-testid="gpay-button"]'
        self.elements.google_pay_iframe = "#pgs-gpay-iframe"
        self.elements.google_pay_email_input = "#identifierId"
        self.elements.google_pay_email_next = "#identifierNext"
        self.elements.google_pay_password_input = "input[name='Passwd']"
        self.elements.google_pay_password_next = "#passwordNext"
        self.elements.google_pay_pay_button = "button:has-text('Pay')"
        # Promotion modal
        self.elements.enter_promo_or_pin_code_button = "[data-testid='apply-promotion-button'],[data-testid='redeem-new-offer-button']"
        self.elements.close_modal_button = "[data-testid='special-offers-modal'] [class^='vn-modal__close'], [data-testid='prepaid-modal'] [class^='vn-modal__close'], [class='vn-modal__close css-kgtk0o']"
        self.elements.promotion_code_input = "[data-testid='code-entry'], [data-testid='promo-code-input-box']"
        self.elements.promotion_apply_button = "button[class*='ApplyButton'], [data-testid='apply-promo-code-button']"
        self.elements.prepaid_value = "[data-testid='prepaid-balance-currency'], [data-testid='replacement-total-prepaid-currency'], [id='benefit-amount']"
        self.elements.raf_months = "[data-testid='refer-a-friend-months']"
        self.elements.ek_months = "[data-testid='enrollment-key-months']"
        self.elements.promo_code_months = "[data-testid='promo-code-months']"
        self.elements.require_billing_message = "[class^='styles__RequireBilling-']"
        self.elements.promo_text = "[class^='styles__EntryPromp']"
        self.elements.special_offer_text = 'text="Special Offers"'
        self.elements.whats_this = '[data-analyticsid="SpecialOffersTooltipLink"]'
        self.elements.whats_this_tooltip = '[role="tooltip"] p'
        self.elements.apply_button = "[data-analyticsid='SpecialOffersApplyButton']"
        self.elements.special_offer_applied_text = 'text="Special Offer Applied."'
        self.elements.refer_a_friend_text = 'text="Refer a Friend"'
        self.elements.one_month = 'text="1 month"'
        self.elements.special_offer_box = "[data-testid='special-offers-box']"
        self.elements.break_down_credits = "[class^='styles__BreakdownTitle-']"
        self.elements.tooltip_link = "[data-analyticsid='SpecialOffersTooltipLink']"
        self.elements.tooltip_content = "[role='tooltip']"
        self.elements.free_trial_months = "[data-testid='free-trial-months']"
        self.elements.plan_details = "[data-testid='itemized-product-info']"
        self.elements.due_now = "[class^='styles__TotalNow-']"
        self.elements.due_after = "[data-testid='total-after-trial']"
        self.elements.tos_link = "[data-analyticsid='InstantInkTosLink']"
        self.elements.here_link = "#ii-arn-component-cancel-url-id"
        self.elements.disclaimer = "[data-testid='plan-description-arn-component']"
        self.elements.back_button_arn = "button[onclick='window.history.back()']"
        self.elements.automatic_renewal_notice = "[data-testid='v3-content-arn-component']"
        self.elements.auto_firmware_update_info = "[data-testid='afu-description-arn-component']"
        self.elements.terms_agreement_checkbox = "[data-testid='terms-agreement']"
        self.elements.enroll_button = "[data-testid='redeem-button']"
        self.elements.support_description_arn_component = "[data-testid='support-description-arn-component']"

        # Billing Card Section locator
        self.elements.billing_info_icon = "[data-analyticsid='billing-card-tooltip']"

        self.elements.billing_card_promo_link = "[data-testid='apply-promotion-button'] > span"
        #self.elements.billing_info_icon_tooltip = "div[class*='root-Tooltip']"
        #self.elements.billing_info_icon_msg = "text=Your billing information is used to continue your subscription after the trial."
        self.elements.billing_header = "text=Billing"
        self.elements.bill_head = "xpath=//*[text()='Select an account type']"
        self.elements.billing_step_one = "text=Step 1 of 2"
        self.elements.address_preview_card = "div[data-testid='address-preview-card']"
        self.elements.account_type_section = "[class*='styles__StyledAccountTypeSection']"
        self.elements.credit_card_payment_box = "[data-testid='credit-card-payment-box']"
        self.elements.shipping_info = "[class*='styles__StyledShippingInfo'] > div:first-of-type"
        self.elements.see_details="xpath=//p[@data-testid='benefits-header']//..//a"
        #billing step two locators
        self.elements.billing_step_two = "text=Step 2 of 2"
        self.elements.Complete_your_payment_ = "text=Complete your payment."

        # Preenroll Select a plan page elements
        self.elements.plan_type_title = 'text=Select a plan type'
        self.elements.pay_as_you_print_card = '[data-testid="i_pay_as_you_print-type-card-content-container"]'
        self.elements.pay_as_you_print_select_btn = '[data-testid="i_pay_as_you_print-plan-type-card-select-button"]'
        self.elements.monthly_plan_card = '[data-testid="i_ink-type-card-content-container"]'
        self.elements.most_popular_plan_identifier = '[data-testid="card-label-i_ink"]:has-text("MOST POPULAR")'
        self.elements.yearly_plan_card = '[data-testid="i_yearly_ink-type-card-content-container"]'
        self.elements.best_savings_plan_identifier = '[data-testid="card-label-i_yearly_ink"]:has-text("BEST SAVINGS")'
        self.elements.yearly_plan_select_btn = '[data-testid="i_yearly_ink-plan-type-card-select-button"]'

        # Preenroll elements
        self.elements.preenroll_continue_button = "[data-testid='preenroll-continue-button']", '[data-testid="printer-enroll-continue-button"]'
        self.elements.connect_later_button = "[data-testid='connect-later-button']"
        self.elements.go_back_button = "[data-testid='go-back-button']"
        self.elements.monthly_plan_title = '//h1[text()="Monthly plans"]'
        self.elements.current_plan_text = '//*[text()="Current page plan selection:"]'
        self.elements.plan_selection_box = '//div[@class="label css-iv5ce9"]'
        self.elements.ink_plan_card = '//div[@class="styles__ItemsContainer-@jarvis/react-instant-ink-plans__sc-1vubsqb-1 jyTNSO"]'
        self.elements.ink_selection_button = '//button[@data-testid="select-plan-ink-only"]'
        self.elements.ink_paper_plan_card = '//div[@class="styles__ItemsContainer-@jarvis/react-instant-ink-plans__sc-1vubsqb-1 iOdFYp"]'
        self.elements.ink_paper_selection_button = '//button[@data-testid="select-plan-ink-and-paper"]'
        self.elements.review_plan_card_description = '[data-testid="plan-card"] [class^="styles__Content"]'
        self.elements.monthly_plan_oobe_title = 'text=Select your printing plan'
        self.elements.plan_modal_subtitle = 'span[data-testid="ii-ink"]'

        # Confirmation page elements
        self.elements.edit_plan_button = "[data-testid='edit-plan']"
        self.elements.edit_shipping_button = '[data-testid="edit-shipping"]'
        self.elements.continue_enrollment_button = "[data-testid='printer-enroll-continue-button'], [data-testid='oobe-enroll-continue-button'], [data-testid='ftm-enroll-continue-button'], [data-testid='oobe-replacement-confirmation-continue-button'], div[class*='ButtonSection'] button:nth-of-type(2)"
        self.elements.hp_checkout_button = "[data-testid='choose-HP-checkout']"
        self.elements.summary_benefits_header = "[data-testid='benefits-header']"
        self.elements.total_due_after_trial = '[data-testid="total-after-trial"]'
        self.elements.terms_agreement_checkbox = "[data-testid='terms-agreement'], [data-testid='enroll-without-billing-terms-agreement']"
        self.elements.prepaid_terms_agreement_checkbox = "[data-testid='prepaid-terms-agreement']"
        self.elements.enroll_button = "[data-testid='redeem-button'],[data-testid='ftm-redesign-enroll-continue-button']"
        self.elements.skip_trial_button = "[data-testid='skip-trial-button']"
        self.elements.skip_trial_modal = "[data-testid='skip-trial-modal']"
        self.elements.skip_paper_offer = "[data-testid='skip-paper']"
        self.elements.message_add_billing_info = "[class^='styles__Description-@jarvis/react-smb-instant-ink']:has-text('Optional: Add your billing information to avoid service interruptions')"
        self.elements.billing_card = "[data-testid='billing-card'], [data-testid='billing-container']"
        self.elements.billing_card_black_tick = '//*[@data-testid="billing-card"]/div/*[@fill="currentColor"]'
        self.elements.billing_card_title = '[data-testid="billing-card"] [class^="styles__Title"]'
        self.elements.billing_card_description = '[data-testid="billing-card"] [class^="styles__Description"]'
        self.elements.paypal_checkout_button_iframe = "iframe[src*='paypal.com/smart/button']"
        self.elements.paypal_checkout_button = "img.paypal-button-logo-paypal"
        self.elements.paypal_phone_modal_textbox = "[data-testid='phone-modal-text-box']"
        self.elements.paypal_phone_modal_submit = "[data-testid='signup-missing-phone-modal'] span"
        # self.elements.paypal_use_password_instead_button = "xpath=//*[@id='identity_auth_provider']/main/div[1]/div[4]/form[2]/button"
        self.elements.paypal_use_password_instead_button = "xpath=//button[@data-atomic-wait-intent='Use_Another_Login_Method']"
        self.elements.paypal_use_password_instead_option = "xpath=//*[text()='Use password instead']"
        self.elements.paypal_addeed_email = '[data-testid="paypal-email"]'
        self.elements.paypal_added_icon = '[class^="styles__PaypalContainer-] svg'
        self.elements.add_paper="[data-testid='add-paper'],[data-testid='paper-addon-checkbox']"
        self.elements.remove_paper="[data-testid='remove-paper'],[data-testid='paper-addon-checkbox']"
        self.elements.oobe_enroll_back_button="[data-testid='oobe-enroll-back-button']"
        self.elements.Tos_link_ARN="xpath=//p[@data-testid='terms-agreement-label']//a[contains(text(),'Terms of Service')]"

        # your plan card
        self.elements.planc_value = 'p[class^="styles__PricePerMonth-@jarvis/react-smb-instant-ink-signup_"]'
        self.elements.plan_pages = 'p[class^="styles__PagesPerMonth-@jarvis/react-smb-instant-ink-signup_"]'
        self.elements.plans_consumer_plan_content_container = '[data-testid="plans-consumer-plan-content-container"]'

        self.elements.checkout_enroll_summary = '[data-testid="automatic-renewal-text"] > p:nth-child(3),[data-testid="payment-description-arn-component"]'
        

        # Flip Elements
        self.elements.skip_free_months = "[data-testid='refuse-button']"
        self.elements.auto_fill_address = "[data-testid='autofill-input']"
        self.elements.paypal_link = "[data-testid='pay-pal-link']"
        self.elements.flip_start_free_trial = "[data-testid='ftm-redesign-enroll-continue-button']"
        self.elements.flip_skip_button = "[data-testid='flip-skip-button']"
        self.elements.flip_terms_agreement_checkbox = "xpath=//input[@data-testid[contains(.,'terms-agreement')] and @class='css-1l5ptj2-interactive'] //..//span[@class='vn-checkbox__span css-pq8vvd-base-base-Checkbox']"
        self.elements.flip_next_button = "[data-testid='next-button']"
        self.elements.flip_close_button= "xpath=//button[@aria-label='Close modal']"
        self.elements.address_option = "xpath=//span[@id='address-option-0']"
        #self.elements.cancel_button="[data-testid='cancel-button']"
        self.elements.shipping_step_title="[data-testid='ftm-shipping-step-title']"
        self.elements.enter_address_manually = "[data-testid='manually-link']"
        self.elements.add_paper_to_your_plan = "[data-testid='paper-addon-checkbox'] + .vn-checkbox__span"
        self.elements.paper_addon_learn_more = "[data-testid='paper-addon-learn-more'], [data-testid='learn-more']"
        self.elements.flip_paper_addon_container = "[data-testid='flip-paper-addon-container'], [data-testid='paper-addon-section']"
        self.elements.learn_more_faq_back_button = "[data-testid='paper-faq-modal-content'] [data-testid='learn-more-faq-back-button']"
        self.elements.add_tax_id_button="[data-testid='add-tax-id-button']"
        self.elements.view_offer="[data-testid='back-to-offer-button']"
        self.elements.remind_me="[data-testid='remind-later-button']"
        self.elements.skip_offer_link="[data-testid='skip-offer-link']"
        self.elements.enroll_step_skip_button="[data-testid='enroll-step-skip-button']"
        self.elements.before_you_go="//div[@class='vn-modal--body css-kfijvp-body-align-Modal']//div//h3"
        self.elements.flip_shipping_container="[data-testid='shipping-container']"
        self.elements.special_offer_text = "p[class='styles__RequireBilling-@jarvis/react-smb-instant-ink-signup__w7xsxk-12 jcenlh']"

        #enrollsummary_header
        self.elements.header_logo='[alt="HP Instant Ink"]'
        self.elements.virtual_assistant='[data-testid="virtual-agent-link"]'
        self.elements.support_phone_number='[data-testid="support-phone-number-link"]'
        self.elements.account_button='[data-testid="account-button"]'
        #self.elements.country_button='[data-testid="country-selector-button"]'
        self.elements.sign_out_link='[data-testid="sign-out-button"]'
        self.elements.country_sector = '[data-testid="country-selector-button"]'
        self.elements.modal_header='[class="styles__CountrySelectorLabel-@jarvis/react-instant-ink-country-selector__sc-1ozjqnh-1 Kutoo"]'
        self.elements.country_dropdown='[id="vn-select-:rc:"]'
        self.elements.language_dropdown='[id="vn-select-:re:"]'
        self.elements.country_options='[role="option"]'
        self.elements.language_options='[id="vn-select-:re:"]'
        self.elements.enroll_step_page = '[data-testid="enroll-step"]'

    def select_ink_plan(self, plan_pages: str):
        plan_selector = f"label:has([data-testid='plan-radio-button-i_ink-{plan_pages}'])"
        self.page.locator(plan_selector).click()

    def select_paper_plan(self, plan_pages: str):
        plan_selector = f"label:has([data-testid='plan-radio-button-i_ink_paper-{plan_pages}'])"
        self.page.locator(plan_selector).click()
