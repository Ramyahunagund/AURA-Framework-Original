from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class ShippingBillingPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Shipping section
        self.elements.manage_shipping_address = "[class^='styles__StyledButtonContainer-@monetization/shipping-billing-management-react__'] a"
        self.elements.shipping_form_modal = "#shipping-content-container"
        self.elements.shipping_section = '[class^="styles__ShippingAddressContainer-@monetization/shipping-billing-management-react"]'
        self.elements.go_back_unsupported_shipping = '[data-testid="unsupported-postal-code-modal-go-back-button"]'
        self.elements.error_message = '[class^="styles__ErrorMessage"]'
        self.elements.first_name_field = '[data-testid="first-name"]'
        self.elements.zip_code_field = '[data-testid="zip-code"]'
        self.elements.street1 = '[data-testid="street1"]'
        self.elements.state = '[data-testid="state"] input'
        self.elements.suggested_address_option = 'input[data-testid="suggested-address"]'
        self.elements.original_address_option = 'input[data-testid="original-address"]'
        self.elements.save_button = '[data-testid="save-button"]'
        self.elements.ship_to_this_address = '[data-testid="ship-to-address-button"]'
        self.elements.saved_address = 'p[class^="styles__StyledContent-@monetization/shipping-billing-management-react_"]'
        self.elements.cancel_address_button = '[data-testid="cancel-button"]'

        # Billing section
        self.elements.manage_your_payment_method_link = "[class^='styles__ManagePaymentText-@monetization/shipping-billing-management'] ,[data-testid='addBillingButton']"
        self.elements.billing_section = '[class^="styles__BillingCard-@monetization/shipping-billing-management-"]'
        self.elements.billing_form_modal = "[data-testid='billing-form-provider']"
        self.elements.add_payment_method = '[data-testid="addBillingButton"]'
        self.elements.address_billing_form_modal = '[data-testid="address-section"]'
        self.elements.paypal_logo = '[class^="styles__StyledPayPalLogo"]'
        # Page elements
        self.elements.page_title = "[class^='styles__StyledMainTitle-@monetization/shipping-billing-management']"
        self.elements.cancel_button = "[data-testid='cancel-button']"
        self.elements.update_shipping_billing_message = '[class^="styles__NotificationContainer"]'
        self.elements.close_modal_button = '[class^="vn-modal__close"]'
        # Billing modal
        self.elements.input_first_address = '#street1'
        self.elements.input_second_address = '#street2'
        self.elements.continue_button = '[data-testid="continue-button"]'
        self.elements.input_card_number = '#txtCardNumber'
        self.elements.billing_address_error_message = '[class^="styles__StyledErrorMessageInline-"]'
        self.elements.credit_card_invalid_error_message = '#mp-message'
        self.elements.billing_modal_iframe = '#pgs-iframe,#challengeFrame'
        self.elements.billing_next_button = "#btn_pgs_card_add"
        self.elements.business_radio_button = '[data-testid="business-radio-button"]'
        self.elements.company_name = '[name="company-name"]'
        self.elements.card_type_icon = '[data-testid="card-type-icon"]'

    @staticmethod
    def select_business_account_type(page):
        """Selects the business account type radio button"""
        page.locator('[data-testid="business-radio-button"]').first.click(force=True)