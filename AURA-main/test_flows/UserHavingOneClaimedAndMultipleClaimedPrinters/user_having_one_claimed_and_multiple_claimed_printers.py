# test_flows/CreateIISubscription/create_ii_subscription.py

import os
import time
import random
import string
import base64
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from core.playwright_manager import PlaywrightManager
from core.settings import GlobalState
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from pages.confirmation_page import ConfirmationPage
from pages.printer_selection_page import PrinterSelectionPage
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def user_having_one_claimed_and_multiple_claimed_printers(stage_callback):
    framework_logger.info("=== C44260650, User having one claimed and multiple claimed printers flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # 1) HPID signup + UCDE onboarding in the same browser context/page
    framework_logger.info("Starting HPID signup and UCDE onboarding in the same window")
    with PlaywrightManager() as page:
        page = common.create_hpid(page, lambda: stage_callback("landing_page", page))
        time.sleep(5)
        framework_logger.info(f"Before UCDE onboarding, current page URL: {page.url}")
        page = common.onboard_hpid_to_ucde(page)

        # 2) Claim virtual printer
        printer = common.create_and_claim_virtual_printer()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            
            # printer validation
            confirmation_page = ConfirmationPage(page)
            printer_selection = PrinterSelectionPage(page)
            page.wait_for_selector(printer_selection.elements.printer_selection_page, state="visible", timeout=180000)
            assert printer_selection.printer_radio_button_input.count() == 2, f"Expected cards, but found {printer_selection.printer_radio_button.count()}"
            assert printer_selection.add_printer.is_visible(), "Add printer button is not visible"
            assert printer_selection.printer_radio_button.nth(1).locator('input').is_checked() == True, "Expected printer card to be selected by default"
            assert printer_selection.continue_button.is_enabled(), "Continue button is not enabled"
            EnrollmentHelper.printer_card_validation(page,[printer])
            EnrollmentHelper.add_card_validation(page)
            # add printer validation
            printer_selection.printer_radio_button.nth(2).click()
            assert printer_selection.continue_button.is_enabled(), "Continue button is not enabled"
            printer_selection.continue_button.click()
            confirmation_page.wait.monthly_plan()
            page.go_back()
            # printer validation
            printer_selection.wait.continue_button()
            printer_selection.printer_radio_button.nth(1).click()
            printer_selection.wait.continue_button().click()
            confirmation_page.wait.monthly_plan()


            printer2 = common.create_and_claim_virtual_printer()
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            assert printer_selection.printer_radio_button_input.count() == 3
            assert printer_selection.printer_radio_button.locator('input')
            EnrollmentHelper.printer_card_validation(page,[printer, printer2])
            EnrollmentHelper.add_card_validation(page)
            # add printer validation
            printer_selection.printer_radio_button.nth(3).click()
            assert printer_selection.continue_button.is_enabled(), "Continue button is not enabled"
            printer_selection.continue_button.click()
            confirmation_page.wait.monthly_plan()
            page.go_back()
            # printer validation
            printer_selection.wait.continue_button()
            printer_selection.printer_radio_button.nth(1).click()
            printer_selection.wait.continue_button().click()
            confirmation_page.wait.monthly_plan()

            # arrows validation
            common.create_and_claim_virtual_printer()
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)
            assert common.is_element_actionable(page, printer_selection.add_printer) is False
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(1)) is True
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(2)) is True
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(3)) is True
            printer_selection.wait.arrow_next_button().click()
            printer_selection.wait.arrow_back_button()
            time.sleep(2)
            assert common.is_element_actionable(page, printer_selection.add_printer) is True
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(1)) is False
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(2)) is False
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(3)) is False
            printer_selection.wait.arrow_back_button().click()
            printer_selection.wait.arrow_next_button()
            time.sleep(2)
            assert common.is_element_actionable(page, printer_selection.add_printer) is False
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(1)) is True
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(2)) is True
            assert common.is_element_actionable(page, printer_selection.printer_radio_button.nth(3)) is True
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
