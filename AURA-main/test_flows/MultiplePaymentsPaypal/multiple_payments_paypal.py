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
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect   
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def multiple_payments_paypal(stage_callback):
    framework_logger.info("=== C39385620 Multiple Payments Paypal flow started ===")
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

        # 2) Claim virtual printer and add address
        common.create_and_claim_virtual_printer_and_add_address()

    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment_and_sign_in(page, tenant_email)

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # plans
            EnrollmentHelper.select_plan(page, 100)
            framework_logger.info(f"Plan selected: 100")

            # billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing added")

            confirmation_page = ConfirmationPage(page)
            confirmation_page.wait.edit_billing_button()

            expect(confirmation_page.edit_billing_button).to_be_visible
            expect(confirmation_page.paypal_addeed_email).to_be_visible
            expect(confirmation_page.paypal_added_icon).to_be_visible

            confirmation_page.edit_billing_button.click()

            assert confirmation_page.credit_card_radio_option.locator('input').is_checked() == True, f"Credit card radio option is not checked by default"

        except Exception as e:
            framework_logger.error(f"An error occurred during the enrollment: {e}\n{traceback.format_exc()}")
            raise e
