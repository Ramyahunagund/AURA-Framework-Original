import os
import time
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


def enroll_summarypage_header(stage_callback):
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
            EnrollmentHelper.select_plan_v3(page, plan_value="100")
            framework_logger.info("Ink only plan selected")

            # APU
            EnrollmentHelper.accept_automatic_printer_updates(page)
            framework_logger.info(f"Automatic Printer Updates accepted")

            #Check the header of Enroll Summary page.
            EnrollmentHelper.header_of_enroll_summary_page(page)
            framework_logger.info(f"Verified the header of Enroll Summary page successfully")

            #Verify a new window is opened and able to chat with "HP virtual agents".
            EnrollmentHelper.clicking_virtual_assistant_link(page)
            framework_logger.info(f"Verified a new window is opened and able to chat with HP virtual agents")

            #Verify the correct phone number info and respective window is shown.
            EnrollmentHelper.verifying_phone_number_link(page)
            framework_logger.info(f"Verified the correct phone number info and respective window is shown successfully")

            #verify country and language sector modal
            EnrollmentHelper.verify_country_sector_modal_dropdown_country(page)
            framework_logger.info(f"Verified country sector modal dropdown successfully")

            #verify the modal is closed on clicking 'X' ifcon
            EnrollmentHelper.verify_closing_country_sector_modal_x(page)

            # verify country and language sector modal
            EnrollmentHelper.verify_country_sector_modal_dropdown_language(page)
            framework_logger.info(f"Verified language sector modal dropdown successfully")

            # verify the modal is closed on clicking 'X' ifcon
            EnrollmentHelper.verify_closing_country_sector_modal_save(page)


            # verify signout link is redirected to consumer landing page
            EnrollmentHelper.verify_signout_link(page)
            framework_logger.info(f"Verified signout link is redirected to consumer landing page")




        except Exception as e:
            framework_logger.error(f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()