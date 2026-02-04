# test_flows/smokes/EnrollmentInkPOOBE/enrollment_ink_poobe.py

from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import time
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

# C29147858
def enrollment_ink_poobe(stage_callback) -> None:
    framework_logger.info("=== Enrollment POOBE flow started ===")
    common.setup()
    tenant_email = common.generate_tenant_email()
    framework_logger.info(f"Generated tenant_email={tenant_email}")

    # Create and register virtual printer
    printer = common.create_virtual_printer()

    # Create account and setup oss emulator
    with PlaywrightManager() as page:
        try:
            page = common.create_ii_v2_account(page)

            # Setup OSS Emulator for POOBE
            OssEmulatorHelper.setup_oss_emulator_poobe_flow(page, printer)
            framework_logger.info(f"OSS Emulator setup completed")

            # Access printing services
            OssEmulatorHelper.accept_connected_printing_services(page)
            framework_logger.info(f"Accepted connected printing services")

            # Continue on value proposition
            OssEmulatorHelper.continue_value_proposition(page)
            framework_logger.info(f"Continued on value proposition page")

            # Accept automatic printer updates
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Accepted automatic printer updates")

            # Select plan
            EnrollmentHelper.select_plan(page, 300)
            framework_logger.info(f"Selected plan 100")

            # Choose HP Checkout
            EnrollmentHelper.choose_hp_checkout(page)
            framework_logger.info(f"Chose HP Checkout")

            # Add Shipping
            EnrollmentHelper.add_shipping(page)
            framework_logger.info(f"Added shipping info")

            # Add Billing
            EnrollmentHelper.add_billing(page)
            framework_logger.info(f"Added billing info")

            # Finish Enrollment
            EnrollmentHelper.finish_enrollment(page)
            framework_logger.info("=== POOBE Enrollment flow completed successfully ===")
        except Exception as e:
            framework_logger.error(f"An error occurred during the POOBE Enrollment flow: {e}\n{traceback.format_exc()}")
            raise e
        finally:    
            page.close()
                  