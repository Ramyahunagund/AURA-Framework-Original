import os
import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
from helper.dashboard_helper import DashboardHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def ii_flip_existing_account_ca(stage_callback):
    framework_logger.info("=== II Flip Existing Account flow started ===")
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

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page, index=1)
            framework_logger.info(f"Shipping added successfully")

            DashboardHelper.access(page)
            framework_logger.info(f"Dashboard accessed successfully")

            OssEmulatorHelper.setup_oss_emulator(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")

            # Accept connected printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")
            #select country
            OssEmulatorHelper.country_select(page)
            framework_logger.info("Selected country")
            #if flex DEcline HP+, if flex and want HP+ activate it 

            EnrollmentHelper.flip_continue(page)
            framework_logger.info("Added shipping info")   
            EnrollmentHelper.add_billing(page)
            framework_logger.info("Added billing info")
            
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== Enrollment completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
        