
from playwright.sync_api import sync_playwright
from core.playwright_manager import PlaywrightManager
from core.settings import framework_logger
from helper.enrollment_helper import EnrollmentHelper
from helper.hpid_helper import HPIDHelper
from pages.hpid_page import HPIDPage
import test_flows_common.test_flows_common as common
from playwright.sync_api import expect
import urllib3
import traceback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TEMP_DIR = "temp"

def partial_mandatory_fields(stage_callback):
    framework_logger.info("=== C40671679 PartialMandatoryFields flow started ===")
    common.setup()
    with PlaywrightManager() as page:
        try:
            EnrollmentHelper.start_enrollment(page)
            HPIDHelper.dismiss_select_country(page)
            hpid_page = HPIDPage(page)
            hpid_page.wait.create_account_button_data(timeout=20000).click()
            framework_logger.info(f"Clicked on Create Account button to start creating account")

            hpid_page.wait.create_account_button(timeout=20000).click()
            framework_logger.info(f"Clicked on Create Account button with the fields empty")

            expect(hpid_page.firstName_helper_text).to_be_visible()
            expect(hpid_page.lastName_helper_text).to_be_visible()
            expect(hpid_page.email_helper_text).to_be_visible()
            expect(hpid_page.password_helper_text).to_be_visible()
        except Exception as e:
            framework_logger.error(f"An error occurred during the flow: {e}\n{traceback.format_exc()}")
            raise e

