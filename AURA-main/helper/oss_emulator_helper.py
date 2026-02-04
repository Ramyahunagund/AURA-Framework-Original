import re
import time
import base64
import test_flows_common.test_flows_common as common
from pages.oss_emulator_page import OssEmulatorPage
from core.settings import framework_logger, GlobalState
from asyncio import wait
from playwright.sync_api import expect

class OssEmulatorHelper:
    @staticmethod
    def access_oss_emulator(page):
        page.goto(common._oss_url)
        page.wait_for_load_state("load", timeout=60000)

    @staticmethod
    def sign_in_oss_emulator(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.dev_tab.click()
        oss_emulator_page.oss_hpid_login.click()

    @staticmethod
    def click_3m_button(page):
        oss_emulator_page = OssEmulatorPage(page)
        time.sleep(5)
        oss_emulator_page.yeti_3m.click(timeout=60000)
    
    @staticmethod
    def fill_oss_emulator(page, printer):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.serial_number.fill(printer.entity_id)
        oss_emulator_page.sku.fill(printer.model_number)
        oss_emulator_page.uuid.fill(printer.device_uuid)
        oss_emulator_page.cloud_id.fill(base64.b64decode(printer.postcard).decode('utf-8'))
        oss_emulator_page.fingerprint.first.fill(base64.b64decode(printer.fingerprint).decode('utf-8'))       
        oss_emulator_page.language_config.select_option("completed")
        oss_emulator_page.country_config.select_option("completed")
    
    @staticmethod
    def select_app_type(page, app_type: str = None):
        app_type = common._simulator_platform  or "Gotham"     
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.app_tab.click()
        oss_emulator_page.app_type.select_option(app_type)

    @staticmethod
    def start_oss_emulator(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.start_flow_button.click()

    @staticmethod
    def setup_oss_emulator(page, printer):
        OssEmulatorHelper.access_oss_emulator(page)
        OssEmulatorHelper.sign_in_oss_emulator(page)
        OssEmulatorHelper.click_3m_button(page)
        OssEmulatorHelper.fill_oss_emulator(page, printer)
        OssEmulatorHelper.select_app_type(page)
        OssEmulatorHelper.start_oss_emulator(page)

    @staticmethod
    def setup_poobe_flow(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.app_post_oobe_agreements_features.click()
        oss_emulator_page.subscription_checkbox.click()
        oss_emulator_page.oobe_checkbox.click()

    @staticmethod
    def setup_oss_emulator_poobe_flow(page, printer):
        OssEmulatorHelper.access_oss_emulator(page)
        OssEmulatorHelper.sign_in_oss_emulator(page)
        OssEmulatorHelper.click_3m_button(page)
        OssEmulatorHelper.fill_oss_emulator(page, printer)
        OssEmulatorHelper.select_app_type(page)
        OssEmulatorHelper.setup_poobe_flow(page)
        OssEmulatorHelper.start_oss_emulator(page)

    @staticmethod
    def accept_connected_printing_services(page):
        oss_emulator_page = OssEmulatorPage(page)
        page.wait_for_load_state("load", timeout=120000)
        oss_emulator_page.accept_all_button.click()

    @staticmethod
    def decline_hp_plus(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.do_not_activate_hp_plus.last.click(timeout=120000)
        oss_emulator_page.decline_hp_plus.click()

    @staticmethod
    def continue_dynamic_security_notice(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.ds_continue_button.click(timeout=200000)

    @staticmethod
    def continue_value_proposition(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.next_button.click(timeout=120000)

    @staticmethod
    def select_replace_printer_and_continue(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.replace_printer_radio_button.nth(1).click()
        oss_emulator_page.continue_button.click()

    @staticmethod
    def activate_hp_plus(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.Hp_Plus_Continue_button.click()
        oss_emulator_page.Activate_HP_Plus.click()

    @staticmethod
    def country_select(page):
        oss_emulator_page = OssEmulatorPage(page)
        select_country = page.locator(f"[id='{GlobalState.country_code}']" )
        try:
            select_country.scroll_into_view_if_needed()
            if select_country.is_visible(timeout=100000):
                framework_logger.info(f"Country is visible {GlobalState.country_code}")
                select_country.click()
                oss_emulator_page.continue_selection.click()
            time.sleep(10)
        except:
            pass

    @staticmethod
    def verify_reminder_checkbox_and_trial_text(page, expected_months):
        reminder_checkbox = page.locator('[data-testid="instant-ink-reminder"]')
        expect(reminder_checkbox).to_be_visible(timeout=500000)
        expect(reminder_checkbox).to_be_checked(timeout=2000)
        reminder_text_locator = page.locator('[class^="styles__CheckBoxText"]')
        expect(reminder_text_locator).to_have_text(re.compile(rf"Remind me 2 weeks before my {expected_months}-month trial of HP Instant Ink expires."))
        trial_info_locator = page.locator('[data-testid="general-monthly-fee-disclaimer"]')
        expect(trial_info_locator).to_be_visible()
        expect(trial_info_locator).to_have_text("After the trial, a monthly fee will be automatically charged unless canceled.")

    @staticmethod
    def access_learn_more(page):
        oss_emulator_page = OssEmulatorPage(page)
        oss_emulator_page.learn_more_button.click(timeout=120000)
