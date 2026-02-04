from playwright.sync_api import Page
from pages.base_page_object import BasePageObject

class OssEmulatorPage(BasePageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        # Dev Tab
        self.elements.dev_tab = "//a[normalize-space(text())='Dev']"
        self.elements.oss_hpid_login = "#oss-hpid-login"
        self.elements.sign_in_button = "#sign-in"
        self.elements.username_input = "#username"
        self.elements.user_name_form_submit = "#user-name-form-submit"
        self.elements.password_input = "#password"
        self.elements.novelli_button = "#novelli"
        self.elements.app_post_oobe_agreements_features = "//a[normalize-space(text())='App/Post-OOBE/Agreements/Features']"
        # Quick Options
        self.elements.yeti_3m = "[id='3m']"
        # Device Tab
        self.elements.serial_number = "#serial-number"
        self.elements.sku = "#sku"
        self.elements.uuid = "#uuid"
        self.elements.cloud_id = "//input[@ng-model='device.cloudID']"
        self.elements.fingerprint = "//input[@id='cdm-printer-fingerprint']"
        self.elements.registration_state = "#registration-state"
        self.elements.usage_tracking_consent = "#usage-tracking-consent"
        self.elements.language_config = "#language-config"
        self.elements.country_config = "#country-config"
        self.elements.load_main_tray = "#load-main-tray"
        self.elements.insert_ink = "#insert-ink"
        self.elements.calibration = "#calibration"
        # App Tab
        self.elements.app_tab = "[data-for='app']"
        self.elements.app_type = "#app-type"
        self.elements.app_type_label = "App Type"
        # Page Elements
        self.elements.start_flow_button = "#start-flow-button"
        # Offers Elements
        self.elements.accept_all_button = "#consent-accept-all-button"
        self.elements.Hp_Plus_Continue_button = "[ng-click='showRequirementsPage()']"
        self.elements.Activate_HP_Plus="[event-id='activate']"
        self.elements.do_not_activate_hp_plus = "[ng-click='showDecline()']"
        self.elements.decline_hp_plus = "[event-id='decline-hp+']"
        self.elements.ds_continue_button = "[event-id='dynamic-security-notice-hp+']"
        self.elements.next_button = "[data-testid='next-button']"
        self.elements.learn_more_button = "[data-testid='learn-more-button']"
        self.elements.value_prop_title = '[data-testid="value-prop-title"]'
        self.elements.instant_ink_reminder = "[data-testid='instant-ink-reminder']"
        self.elements.value_prop_learn_more = "[data-testid='learn-more-button']"
        # Post-OOBE Elements
        self.elements.subscription_checkbox = 'input[ng-model="ossInstallData.features.inkSubscription"] ~ span'
        self.elements.oobe_checkbox = 'input[ng-model="ossInstallData.oobe"] ~ span'
        # Click radio button "Replace Printer" and continue button
        self.elements.replace_printer_radio_button = "[class^='vn-radio-button__icon']"
        self.elements.continue_button = "button[data-analyticsid='continue-button']"
        self.elements.continue_selection = "[class='btn-primary ng-binding btn-enabled']"
