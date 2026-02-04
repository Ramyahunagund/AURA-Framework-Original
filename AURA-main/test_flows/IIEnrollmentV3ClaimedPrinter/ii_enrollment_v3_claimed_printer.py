# test_flows/EnrollmentInkWebPaper/enrollment_ink_web_paper.py

import os
import time
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from core.settings import GlobalState
from core.settings import framework_logger
from core.playwright_manager import PlaywrightManager
from helper.dashboard_helper import DashboardHelper
from helper.enrollment_helper import EnrollmentHelper
from helper.gemini_ra_helper import GeminiRAHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_enrollment_v3_claimed_printer(stage_callback):
    framework_logger.info("=== Enrollment Ink Web Paper flow started ===")
    common.setup()
    test_requirements = GlobalState.requirements
    plan_pages = test_requirements.get("plan_pages")
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant.email={tenant_email}")

    with PlaywrightManager() as page:
        try:
            # Create a new HPID account
            page = common.create_ii_v2_account(page)

            # Create and Claim virtual printer
            common.create_and_claim_virtual_printer()

            time.sleep(600) # wait for 10 minutes to ensure printer is claimed before starting enrollment

            # Start Instant Ink Web enroll flow
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value
            
            time.sleep(90)
             
            # accept TOS
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info(f"Terms of Services accepted")  

            time.sleep(60)      

            # printer selector method
            EnrollmentHelper.select_printer(page)
            framework_logger.info(f"Printer selected")

            EnrollmentHelper.validate_plan_page_header_elements(page)
            framework_logger.info(f"Plan page header elements validated successfully")

            # Select paper plan
            EnrollmentHelper.select_plan(page, "100", "ink_and_paper")
            framework_logger.info(f"Paper plan selected: 100")

            EnrollmentHelper.validate_plan_price(page,["10","50","100","300","700"],["$2.78","$7.98","$12.48","$22.98","$44.98"],ink_and_paper=True)
            framework_logger.info(f"Plan prices validated successfully")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Step 5: Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Step 6: Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            EnrollmentHelper.select_plan(page, plan_pages, "ink_and_paper")
            framework_logger.info(f"Paper plan selected: {plan_pages}")

            EnrollmentHelper.edit_shipping(page)
            EnrollmentHelper.add_shipping(page,index=1)
            framework_logger.info(f"Edited shipping successfully")

            EnrollmentHelper.edit_billing(page)
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Edited billing successfully")
            time.sleep(20)

            offer = common.get_offer(GlobalState.country_code)
            identifier = offer.get("identifier")
            if not identifier:
                raise ValueError(f"No identifier found for region: {GlobalState.country_code}")

            ek_code = common.offer_request(identifier)
            EnrollmentHelper.apply_and_validate_ek_code(page, ek_code)
           
            EnrollmentHelper.apply_and_validate_promo_code(page, "freeinkautonew2025")
            
            EnrollmentHelper.apply_and_validate_raf_code(page, "2nbdy7")
            
            framework_logger.info(f"EK, Promo and RAF codes applied successfully")
            # Step 7: Finish Enrollment
            EnrollmentHelper.finish_enrollment(page)           
            framework_logger.info("Ink web enrollment paper completed successfully")
    
        except Exception as e:
            framework_logger.error(f"An error occurred during the Ink Web Enrollment Paper: {e}\n{traceback.format_exc()}")
            raise e
                     