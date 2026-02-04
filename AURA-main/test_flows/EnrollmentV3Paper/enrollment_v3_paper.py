import os
import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.enrollment_helper import EnrollmentHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def enrollment_v3_paper(stage_callback):
    framework_logger.info("=== Enrollment V3 Paper flow started ===")
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

            # Select Ink and Paper Plan V3
            EnrollmentHelper.select_plan_v3(page, plan_value=100, paper=True)
            framework_logger.info("Ink and paper plan selected")

            # APU 
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            # Verify total due after trial
            EnrollmentHelper.validate_total_due_after_trial(page, value="12.48")
            framework_logger.info(f"Total due after trial verified")

            # Connect printer page
            EnrollmentHelper.connect_printer(page)
            framework_logger.info("Connect Printer page")

            # Fill OSS Emulator data
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info("OSS Emulator setup completed")

            # Complete the enrollment v3
            EnrollmentHelper.accept_all_preferences(page)
            framework_logger.info("All preferences accepted")

            # Decline HP+ offer
            OssEmulatorHelper.decline_hp_plus(page)
            framework_logger.info(f"Declined HP+")

            # Continue on dynamic security notice
            OssEmulatorHelper.continue_dynamic_security_notice(page)
            framework_logger.info(f"Continued on dynamic security notice")

            page.wait_for_timeout(120000)

            # Finish enrollment V3 Paper flow
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment V3 Paper flow finished successfully")
        except Exception as e:
            framework_logger.error(f"An error occurred during the Enrollment V3 Paper flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
