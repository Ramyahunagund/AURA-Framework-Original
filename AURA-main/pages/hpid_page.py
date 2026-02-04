from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class HPIDPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.elements.firstName_helper_text = "#firstName-helper-text"
        self.elements.lastName_helper_text = "#lastName-helper-text"
        self.elements.email_helper_text = "#email-helper-text"
        self.elements.password_helper_text = "#password-helper-text"
        self.elements.create_account_button = "#sign-up-submit"
        self.elements.country_selector_button = "[data-testid='country-selector-buttons-container'] button"
        self.elements.username = "#username"
        self.elements.user_name_form_submit = "#user-name-form-submit"
        self.elements.password = "#password"
        self.elements.sign_in = "#sign-in"
        self.elements.sign_in_option = "[data-testid='hpid-value-prop'] [data-testid='sign-in-button']"
        self.elements.firstName = "#firstName"
        self.elements.lastName = "#lastName"
        self.elements.email = "#email"
        self.elements.market = "#market"
        self.elements.submit_code = "#submit-code"
        self.elements.code = "#code"
        self.elements.create_account_button_data = "[data-testid='create-account-button'], #sign-up"
        self.elements.hpid_value_prop_page = "[data-testid='hpid-value-prop']"
