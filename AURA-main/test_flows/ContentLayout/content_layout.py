import os
import time
from playwright.sync_api import expect
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def content_layout(stage_callback):
    framework_logger.info("=== Enrollment V3 flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # Create virtual printer   
    printer = common.create_virtual_printer()
    
    # Create a new HPID account
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)
        
            # Click on Sign Up Now button
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value

            # Accept Terms of Service
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info("Terms of Service accepted")

            # Select plan type card
            EnrollmentHelper.select_plan_type(page)
            
            # Select Ink plan
            EnrollmentHelper.select_plan_v3(page, plan_value=100)
            framework_logger.info("Ink only plan selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

             # Check that PayPal button should NOT have blue selection styling by default
            expect(page.locator('[data-testid="choose-paypal-express"]')).not_to_have_css("border-color", "blue")
            expect(page.locator('[data-testid="choose-paypal-express"]')).not_to_have_css("background-color", "blue")
            framework_logger.info(f"Verified PayPal button is not selected by default (no blue styling)")

            # Check that HP Checkout button should NOT have blue selection styling by default
            expect(page.locator('[data-testid="choose-HP-checkout"]')).not_to_have_css("border-color", "blue")
            expect(page.locator('[data-testid="choose-HP-checkout"]')).not_to_have_css("background-color", "blue")
            framework_logger.info(f"Verified HP Checkout button is not selected by default (no blue styling)")

            # Check that Continue button is disabled
            expect(page.locator('[data-testid="preenroll-continue-button"]')).to_be_disabled()
            framework_logger.info(f"Verified Continue button is disabled as expected")

            framework_logger.info("=== C42409830 - Add Billing Paypal completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e