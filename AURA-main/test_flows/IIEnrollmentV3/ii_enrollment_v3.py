import os
import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger, GlobalState
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_enrollment_v3(stage_callback):
    framework_logger.info("=== Enrollment V3 flow started ===")
    common.setup()
    test_requirements = GlobalState.requirements
    hpplus_action = test_requirements.get("hpplus")
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

            page.reload()
            time.sleep(30)

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

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Shipping added successfully")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Added successfully")

            EnrollmentHelper.edit_billing(page)
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Billing Edited and Added successfully")

            EnrollmentHelper.edit_shipping(page)
            EnrollmentHelper.add_shipping(page, index=1)
            framework_logger.info(f"Shipping Edited and Added successfully")

            offer = common.get_offer(GlobalState.country_code)
            identifier = offer.get("identifier")
            if not identifier:
                raise ValueError(f"No identifier found for region: {GlobalState.country_code}")

            ek_code = common.offer_request(identifier)
            EnrollmentHelper.apply_and_validate_ek_code(page, ek_code)
            EnrollmentHelper.apply_and_validate_promo_code(page, "freeinkautonew2025")
            EnrollmentHelper.apply_and_validate_raf_code(page, "2nbdy7")
            framework_logger.info(f"EK, Promo and RAF codes applied successfully")
            EnrollmentHelper.see_details_special_offer(page)
            framework_logger.info("See details of special offer")

            # Connect printer
            EnrollmentHelper.connect_printer(page)
            framework_logger.info("Connect Printer page")

            # Setup OSS Emulator for Enrollment V3
            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed for Enrollment V3")

            # Complete the enrollment v3
            EnrollmentHelper.accept_all_preferences(page)
            framework_logger.info("All preferences accepted")

            OssEmulatorHelper.country_select(page)
            framework_logger.info("Selected country")
            #if flex DEcline HP+, if flex and want HP+ activate it
            if GlobalState.biz_model == "Flex" and hpplus_action == "decline":
                OssEmulatorHelper.decline_hp_plus(page)
                framework_logger.info(f"Declined HP+")
                
                # Continue on dynamic security notice
                OssEmulatorHelper.continue_dynamic_security_notice(page)
                framework_logger.info(f"Continued on dynamic security notice")
            
            elif(GlobalState.biz_model == "Flex" and hpplus_action == "activate"):
                OssEmulatorHelper.activate_hp_plus(page)
                framework_logger.info(f"Activated HP+")
            elif(GlobalState.biz_model == "E2E" and hpplus_action == "ignore"):
                framework_logger.info(f"Continued flow")
            else:
                   # Continue with the next steps if neither condition is met
                    framework_logger.info("No HP+ action required, continuing enrollment flow.")  

            # Finish enrollment V3 flow
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("Enrollment V3 flow finished successfully")
        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
         