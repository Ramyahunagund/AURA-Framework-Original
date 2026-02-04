from core.playwright_manager import PlaywrightManager
from pages.privacy_banner_page import PrivacyBannerPage
from pages.landing_page import LandingPage

import traceback
from playwright.sync_api import expect
from core.settings import framework_logger
import test_flows_common.test_flows_common as common
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enrolment_kit_banner_not_visible(stage_callback):   
    framework_logger.info("=== Enrolment Kit Banner Not Visible validation started ===")
    common.setup()

    timeout_ms = 120000

    with PlaywrightManager() as page:
        try:
            privacy_banner_page = PrivacyBannerPage(page)
            landing_page = LandingPage(page)
      
            # Step 1: Launch the Consumer Landing page           
            page.goto(common._instantink_url, timeout=timeout_ms)
            privacy_banner_page.accept_privacy_banner()
            expect(landing_page.header_logo).to_be_visible(timeout=timeout_ms)
            framework_logger.info("Launch the Consumer Landing page")

            framework_logger.info("enable_origami_landingpage_for_locales must be disabled")

            # Verify the EK banner is not displayed
            expect(landing_page.ek_banner).not_to_be_visible(timeout=timeout_ms)
            framework_logger.info("Verified the EK banner is not visible")

            # Verify banner content elements are not visible
            expect(landing_page.ek_banner_content).not_to_be_visible()
            expect(landing_page.ek_message_container).not_to_be_visible()
            expect(landing_page.ek_banner_message).not_to_be_visible()
            expect(landing_page.ek_signup_link).not_to_be_visible()
            framework_logger.info("Verified the EK banner content elements are not visible")

            framework_logger.info("=== C38471740 - Enrolment Kit Banner Not Visible validation completed successfully ===")

        except Exception as e:
            framework_logger.error(f"An error occurred during Enrolment Kit Banner Not Visible validation: {e}\n{traceback.format_exc()}")
            raise e
        