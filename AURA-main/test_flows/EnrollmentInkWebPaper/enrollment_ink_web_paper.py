# test_flows/EnrollmentInkWebPaper/enrollment_ink_web_paper.py

import os
import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
from core.playwright_manager import PlaywrightManager
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def enrollment_ink_web_paper(stage_callback):
    framework_logger.info("=== Enrollment Ink Web Paper flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    with PlaywrightManager() as page:
        try:
            # Create a new HPID account
            page = common.create_ii_v2_account(page)

            # Create and Claim virtual printer
            common.create_and_claim_virtual_printer()

            # Start Instant Ink Web enroll flow
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value
                       
            # accept TOS
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info(f"Terms of Services accepted")        

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            # Select paper plan
            EnrollmentHelper.select_plan(page, "100", "ink_and_paper")
            framework_logger.info(f"Paper plan selected: 100")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Step 5: Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Step 6: Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Step 7: Finish Enrollment
            EnrollmentHelper.finish_enrollment(page)           
            framework_logger.info("Ink web enrollment paper completed successfully")
    
        except Exception as e:
            framework_logger.error(f"An error occurred during the Ink Web Enrollment Paper: {e}\n{traceback.format_exc()}")
            raise e
                     