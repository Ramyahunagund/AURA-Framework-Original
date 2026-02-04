import os
import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from pages.confirmation_page import ConfirmationPage
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def v3_pre_enrollment(stage_callback):
    framework_logger.info("=== V3 Pre-Enrollment flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # Create virtual printer   
    printer = common.create_virtual_printer()
    
    # Create a new HPID account
    with PlaywrightManager() as page:
        try:
            # V3 Pre-enroll new account creation: https://hp-testrail.external.hp.com/index.php?/cases/view/61419003
            framework_logger.info("======== C61419003-Create a new account-V3 Pre-enroll========")
            page = common.create_ii_v2_account(page)
            confirmation_page = ConfirmationPage(page)
            ## Click on Sign Up Now button
            with page.context.expect_page() as new_page_info:
                EnrollmentHelper.signup_now(page)
                framework_logger.info("Sign Up Now button clicked")
            page = new_page_info.value
            ## Accept Terms of Service
            EnrollmentHelper.accept_terms_of_service(page)
            framework_logger.info("Terms of Service accepted")
            page.wait_for_timeout(45000)  # Wait for navigation to complete
            assert page.locator(confirmation_page.elements.plan_type_title).is_visible(), "Failed to display Plan type page after accepting Terms of Service"
            framework_logger.info("V3 Account created and Plan type page is displayed")
            stage_callback("ReviewPage_ShippingInfo", page, screenshot_only=True)

            # Plan Type Selection page validation: https://hp-testrail.external.hp.com/index.php?/cases/view/61900610
            framework_logger.info("======== C61900610-Plan Type Selection page validation========")
            EnrollmentHelper.plan_type_page_validation(page, callback=stage_callback)
            framework_logger.info("Validation of Plan Type Selection page elements completed")
            stage_callback("PlanType_SelectionValidation", page, screenshot_only=True)
            #
            # # Select plan type card (monthly plan)
            EnrollmentHelper.select_plan_type(page) # default type is monthly
            #
            # # Select Ink plan
            # EnrollmentHelper.select_plan_v3(page, plan_value=100)
            # framework_logger.info("Ink only plan selected")
            #
            # # APU
            # EnrollmentHelper.accept_automatic_printer_updates(page)
            # framework_logger.info(f"Automatic Printer Updates accepted")
            #
            # # Choose HP Checkout
            # EnrollmentHelper.choose_hp_checkout(page)
            # framework_logger.info(f"Chose HP Checkout")
            #
            # # Add Shipping
            # EnrollmentHelper.add_shipping(page)
            # framework_logger.info(f"Shipping added successfully")
            #
            # # Add Billing
            # EnrollmentHelper.add_billing(page)
            # framework_logger.info(f"Billing Added successfully")
            #
            # # Connect printer
            # EnrollmentHelper.connect_printer(page)
            # framework_logger.info("Connect Printer page")
            #
            # # Setup OSS Emulator for Enrollment V3
            # OssEmulatorHelper.setup_oss_emulator(page, printer)
            # framework_logger.info(f"OSS Emulator setup completed for Enrollment V3")
            #
            # # Complete the enrollment v3
            # EnrollmentHelper.accept_all_preferences(page)
            # framework_logger.info("All preferences accepted")
            #
            # # Decline HP+ offer
            # OssEmulatorHelper.decline_hp_plus(page)
            # framework_logger.info(f"Declined HP+")
            #
            # # Continue on dynamic security notice
            # OssEmulatorHelper.continue_dynamic_security_notice(page)
            # framework_logger.info(f"Continued on dynamic security notice")
            #
            # # Finish enrollment V3 flow
            # EnrollmentHelper.finish_enrollment(page)
            # framework_logger.info("Enrollment V3 flow finished successfully")

            framework_logger.info("All tests passed, closing the browser.")
        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
         