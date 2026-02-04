
import os
import time
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.landing_page_helper import LandingPageHelper
from helper.oss_emulator_helper import OssEmulatorHelper
import test_flows_common.test_flows_common as common
import urllib3
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"


def consumer_landing_page_mobe(stage_callback):
    framework_logger.info("=== Enrollment V3 flow started ===")
    common.setup()
    # tenant_email = common.generate_tenant_email()
    # framework_logger.info(f"Generated tenant_email={tenant_email}")

    # # Create virtual printer
    # printer = common.create_virtual_printer()

    # Create a new HPID account
    with PlaywrightManager() as page:
        try:
            # Resize the window resolution
            page.set_viewport_size({"width": 400, "height": 740})
            framework_logger.info(f"Set viewport size to 400x740")

            framework_logger.info("==== C61418990-Sign Up Now Function ====")
            framework_logger.info("==== C63873538-Other Link Functions ====")
            LandingPageHelper.consumer_landing_page_mobe(page)
            framework_logger.info("==== C63876444-Never worry about running out of ink again ====")
            LandingPageHelper.validate_never_worry_section_mobe(page, stage_callback)
            framework_logger.info("==== C39532972-Hyperlinks ====")
            LandingPageHelper.hyperlinks_validation_mobe(page)
            framework_logger.info("==== C39532988-Cookie Settings ====")
            LandingPageHelper.cookies_settings_mobe(page, stage_callback)

        except Exception as e:
            framework_logger.error(
                f"An error occurred during the V3 Account and Enrollment: {e}\n{traceback.format_exc()}")
            raise e
        finally:
            page.close()
